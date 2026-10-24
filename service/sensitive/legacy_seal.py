#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""把已经落库的明文封存掉。真实 unionid 用完即弃，不写入 Redis。"""
import logging

from sqlalchemy import text

from service.meet_seat import SEAT_BOY, SEAT_GIRL
from util.database import engine
from util.sensitive_cipher import is_sealed_unionid, seal_json, seal_unionid, union_lookup
from util.slot_blind import activity_slot_key

logger = logging.getLogger(__name__)

_EMPTY_STATE = 0
_LINK_TABLES = (
    {
        'table': 'notice_sent',
        'old_index': 'uk_activity_passport_scene',
        'new_index': 'uk_slot_passport_scene',
        'new_ddl': 'ADD UNIQUE KEY `uk_slot_passport_scene` (`slot_key`, `passport_id`, `scene`)',
    },
    {
        'table': 'meet_no_show',
        'old_index': 'uk_passport_activity',
        'new_index': 'uk_passport_slot',
        'new_ddl': 'ADD UNIQUE KEY `uk_passport_slot` (`passport_id`, `slot_key`)',
    },
)
_PLAIN_LINK_TABLES = ('notice_sent', 'meet_no_show', 'meet_fee_order', 'activity_change_record')


def seal_legacy_plaintext():
    logger.info("开始封存仍以明文落库的用户数据")
    with engine.connect().execution_options(isolation_level='AUTOCOMMIT') as conn:
        _ensure_schema(conn)
    with engine.begin() as conn:
        union_by_passport = _legacy_unionids(conn)
        _seal_profiles(conn, union_by_passport)
        _seal_seats(conn, union_by_passport)
        _clear_unkeyed_profiles(conn)
        _clear_unkeyed_activity_passports(conn, set(union_by_passport))
        _seal_identity_rows(conn, union_by_passport)
        _backfill_slots(conn)
        _clear_phones(conn)
    _swap_link_indexes()
    with engine.begin() as conn:
        _zero_link_activity_ids(conn)
    logger.info("明文封存结束")


def seal_passport_plaintext(passport_id, unionid):
    """登录拿到微信 unionid 后，把这个人还没封上的明文补封。"""
    if not passport_id or not unionid:
        return
    with engine.begin() as conn:
        owned = {int(passport_id): unionid}
        _seal_profiles(conn, owned)
        _seal_seats(conn, owned)


def _ensure_schema(conn):
    _ensure_table(conn, 'activity_seat', """
        CREATE TABLE `activity_seat` (
            `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
            `passport_id` BIGINT UNSIGNED NOT NULL DEFAULT 0,
            `slot_key` CHAR(64) NOT NULL DEFAULT '',
            `nonce` VARCHAR(32) NOT NULL DEFAULT '',
            `cipher_text` VARBINARY(512) NOT NULL,
            `status` TINYINT UNSIGNED NOT NULL DEFAULT 1,
            `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`),
            UNIQUE KEY `uk_passport_slot` (`passport_id`, `slot_key`),
            KEY `idx_slot` (`slot_key`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='见面座位。场次在密文里'
    """)
    _ensure_column(conn, 'profile_attr', 'value_nonce',
                   "ALTER TABLE `profile_attr` ADD COLUMN `value_nonce` VARCHAR(32) NOT NULL DEFAULT ''")
    _ensure_column(conn, 'profile_attr', 'value_cipher',
                   "ALTER TABLE `profile_attr` ADD COLUMN `value_cipher` BLOB NULL")
    for table in _PLAIN_LINK_TABLES:
        _ensure_column(conn, table, 'slot_key',
                       "ALTER TABLE `%s` ADD COLUMN `slot_key` CHAR(64) NOT NULL DEFAULT ''" % table)
    logger.info("敏感数据表结构已就绪")


def _legacy_unionids(conn):
    rows = conn.execute(text(
        "SELECT passport_id, secret_material FROM identity_secret "
        "WHERE status=1 AND secret_material<>''"
    )).fetchall()
    found = {}
    for passport_id, material in rows:
        if is_sealed_unionid(material):
            continue
        found[int(passport_id)] = material
    logger.info("待封存身份密钥 count=%s", len(found))
    return found


def _seal_profiles(conn, union_by_passport):
    if not union_by_passport:
        return
    rows = _select_passports(conn, (
        "SELECT id, passport_id, value_min, value_max, value_text, value_cipher "
        "FROM profile_attr WHERE status=1 AND passport_id IN ({ids})"
    ), list(union_by_passport))
    params = []
    for row_id, passport_id, value_min, value_max, value_text, value_cipher in rows:
        if value_cipher or not _has_profile_plain(value_min, value_max, value_text):
            continue
        material = union_by_passport.get(int(passport_id))
        if not material:
            continue
        nonce, cipher = seal_json(material, {
            'value_min': int(value_min or 0),
            'value_max': int(value_max or 0),
            'value_text': value_text or '',
        })
        params.append({'id': row_id, 'nonce': nonce, 'cipher': cipher})
    _execute_many(conn, (
        "UPDATE profile_attr SET value_nonce=:nonce, value_cipher=:cipher, "
        "value_text='', value_min=0, value_max=0 WHERE id=:id"
    ), params)
    logger.info("已封存个人资料 count=%s", len(params))


def _seal_seats(conn, union_by_passport):
    if not union_by_passport:
        return
    rows = _select_passports(conn, (
        "SELECT id, boy_passport_id, girl_passport_id FROM activity "
        "WHERE boy_passport_id IN ({ids}) OR girl_passport_id IN ({ids})"
    ), list(union_by_passport))
    if not rows:
        return
    if not activity_slot_key(rows[0][0]):
        raise RuntimeError('微信密钥为空，无法封存见面座位')
    inserts = []
    clears = []
    for activity_id, boy_id, girl_id in rows:
        slot = activity_slot_key(activity_id)
        boy_id = int(boy_id or 0)
        girl_id = int(girl_id or 0)
        if _queue_seat(inserts, union_by_passport, boy_id, slot, activity_id, SEAT_BOY):
            boy_id = 0
        if _queue_seat(inserts, union_by_passport, girl_id, slot, activity_id, SEAT_GIRL):
            girl_id = 0
        clears.append({'id': activity_id, 'boy': boy_id, 'girl': girl_id})
    _execute_many(conn, (
        "INSERT INTO activity_seat (passport_id, slot_key, nonce, cipher_text, status) "
        "VALUES (:passport_id, :slot_key, :nonce, :cipher_text, 1) "
        "ON DUPLICATE KEY UPDATE nonce=VALUES(nonce), cipher_text=VALUES(cipher_text), status=1"
    ), inserts)
    _execute_many(conn, (
        "UPDATE activity SET boy_passport_id=:boy, girl_passport_id=:girl WHERE id=:id"
    ), clears)
    logger.info("已封存见面座位 count=%s", len(inserts))


def _clear_unkeyed_profiles(conn):
    result = conn.execute(text(
        "UPDATE profile_attr SET value_text='', value_min=0, value_max=0 "
        "WHERE (value_text<>'' OR value_min<>0 OR value_max<>0) "
        "AND (value_cipher IS NULL OR OCTET_LENGTH(value_cipher)=0)"
    ))
    logger.info("已清掉无法封存的资料明文 count=%s", result.rowcount)


def _clear_unkeyed_activity_passports(conn, keyed_ids):
    rows = conn.execute(text(
        "SELECT id, boy_passport_id, girl_passport_id, state FROM activity "
        "WHERE boy_passport_id<>0 OR girl_passport_id<>0"
    )).fetchall()
    if not rows:
        return
    seated = _seated_slots(conn, [activity_slot_key(row[0]) for row in rows])
    params = []
    for activity_id, boy_id, girl_id, state in rows:
        boy_id = int(boy_id or 0)
        girl_id = int(girl_id or 0)
        new_boy = boy_id if boy_id in keyed_ids else 0
        new_girl = girl_id if girl_id in keyed_ids else 0
        if new_boy == boy_id and new_girl == girl_id:
            logger.error("见面护照编号未能封存 activity=%s", activity_id)
            continue
        new_state = state
        if new_boy == 0 and new_girl == 0 and activity_slot_key(activity_id) not in seated:
            new_state = _EMPTY_STATE
        params.append({'id': activity_id, 'boy': new_boy, 'girl': new_girl, 'state': new_state})
    _execute_many(conn, (
        "UPDATE activity SET boy_passport_id=:boy, girl_passport_id=:girl, state=:state WHERE id=:id"
    ), params)
    logger.info("已清掉无法封存的见面护照编号 count=%s", len(params))


def _seal_identity_rows(conn, union_by_passport):
    params = []
    for passport_id, unionid in union_by_passport.items():
        params.append({
            'passport_id': passport_id,
            'account_key': union_lookup(unionid),
            'sealed': seal_unionid(unionid),
        })
    _execute_many(conn, (
        "UPDATE identity_secret SET account_key=:account_key, secret_material=:sealed "
        "WHERE passport_id=:passport_id AND status=1"
    ), params)
    logger.info("已自加密封存身份密钥 count=%s", len(params))


def _backfill_slots(conn):
    params = []
    for table in _PLAIN_LINK_TABLES:
        rows = conn.execute(text(
            "SELECT id, activity_id FROM `%s` WHERE activity_id<>0 AND slot_key=''" % table
        )).fetchall()
        if rows and not activity_slot_key(rows[0][1]):
            raise RuntimeError('微信密钥为空，无法封存见面场次关联')
        for row_id, activity_id in rows:
            slot = activity_slot_key(activity_id)
            if not slot:
                logger.error("见面关联无法计算盲索引 table=%s id=%s", table, row_id)
                continue
            params.append({'table': table, 'id': row_id, 'slot': slot})
        _execute_many(conn, (
            "UPDATE `%s` SET slot_key=:slot WHERE id=:id AND slot_key=''" % table
        ), [{'id': item['id'], 'slot': item['slot']} for item in params if item['table'] == table])
        conn.execute(text(
            "UPDATE `%s` SET slot_key=CONCAT('cleared-', id) WHERE slot_key='' AND activity_id=0" % table
        ))
    logger.info("已补见面盲索引 count=%s", len(params))


def _clear_phones(conn):
    result = conn.execute(text("UPDATE passport SET phone='' WHERE phone<>''"))
    logger.info("已清掉账号上的手机号明文 count=%s", result.rowcount)


def _swap_link_indexes():
    with engine.connect().execution_options(isolation_level='AUTOCOMMIT') as conn:
        for item in _LINK_TABLES:
            indexes = _index_names(conn, item['table'])
            if item['old_index'] in indexes:
                conn.execute(text(
                    "ALTER TABLE `%s` DROP INDEX `%s`" % (item['table'], item['old_index'])
                ))
            if item['new_index'] not in _index_names(conn, item['table']):
                conn.execute(text("ALTER TABLE `%s` %s" % (item['table'], item['new_ddl'])))
    logger.info("见面关联索引已改为盲索引")


def _zero_link_activity_ids(conn):
    for table in _PLAIN_LINK_TABLES:
        result = conn.execute(text(
            "UPDATE `%s` SET activity_id=0 WHERE slot_key<>'' AND activity_id<>0" % table
        ))
        logger.info("已清掉见面关联里的场次编号 table=%s count=%s", table, result.rowcount)


def _queue_seat(inserts, union_by_passport, passport_id, slot, activity_id, role):
    material = union_by_passport.get(passport_id)
    if not passport_id or not material or not slot:
        return False
    nonce, cipher = seal_json(material, {'activity_id': int(activity_id), 'role': int(role)})
    inserts.append({
        'passport_id': passport_id,
        'slot_key': slot,
        'nonce': nonce,
        'cipher_text': cipher,
    })
    return True


def _has_profile_plain(value_min, value_max, value_text):
    return bool(int(value_min or 0) or int(value_max or 0) or str(value_text or '').strip())


def _seated_slots(conn, slots):
    keys = [slot for slot in slots if slot]
    if not keys:
        return set()
    clause, params = _binds('slot', keys)
    rows = conn.execute(text(
        "SELECT slot_key FROM activity_seat WHERE status=1 AND slot_key IN (%s)" % clause
    ), params).fetchall()
    return {row[0] for row in rows}


def _select_passports(conn, sql, passport_ids):
    if not passport_ids:
        return []
    clause, params = _binds('passport', passport_ids)
    return conn.execute(text(sql.format(ids=clause)), params).fetchall()


def _execute_many(conn, sql, params):
    if params:
        conn.execute(text(sql), params)


def _binds(name, values):
    keys = []
    params = {}
    for index, value in enumerate(values):
        key = '%s_%s' % (name, index)
        keys.append(':' + key)
        params[key] = value
    return ', '.join(keys), params


def _ensure_table(conn, table, ddl):
    if table.lower() not in _table_names(conn):
        conn.execute(text(ddl))
        logger.info("已建表 %s", table)


def _ensure_column(conn, table, column, ddl):
    if column.lower() not in _column_names(conn, table):
        conn.execute(text(ddl))
        logger.info("已加列 %s.%s", table, column)


def _table_names(conn):
    rows = conn.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()"
    )).fetchall()
    return {str(row[0]).lower() for row in rows}


def _column_names(conn, table):
    rows = conn.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = :table"
    ), {'table': table}).fetchall()
    return {str(row[0]).lower() for row in rows}


def _index_names(conn, table):
    rows = conn.execute(text(
        "SELECT DISTINCT index_name FROM information_schema.statistics "
        "WHERE table_schema = DATABASE() AND table_name = :table"
    ), {'table': table}).fetchall()
    return {str(row[0]).lower() for row in rows}
