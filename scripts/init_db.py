#!/usr/bin/env python
# coding=utf-8
"""
数据库初始化脚本：幂等执行 DDL + 写入 Mock 测试数据

用法:
  python scripts/init_db.py                             # 本地（读 .env）
  docker-compose exec app python scripts/init_db.py    # 容器内

幂等保证:
  - DDL 使用 CREATE TABLE IF NOT EXISTS，可重复执行
  - Mock 数据通过主键/唯一标识检查，已存在则跳过
"""
import datetime
import logging
import os
import sys

import pymysql

# 支持从项目根目录或 scripts/ 子目录运行
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger(__name__)

DDL_FILE = os.path.join(PROJECT_ROOT, 'sql', 'init', 'init.sql')
# 只执行 sql/migrations/ 下的新增迁移（Docker 时代的增量变更）
# sql/ 根目录下的老文件是历史档案，针对旧 schema，不在此执行
MIGRATION_DIR = os.path.join(PROJECT_ROOT, 'sql', 'migrations')


# ── 连接配置 ───────────────────────────────────────────────────────────────────

def _load_env_file():
    """从 .env 文件加载环境变量（仅当环境变量未设置时生效）"""
    env_path = os.path.join(PROJECT_ROOT, '.env')
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            if key not in os.environ:  # 不覆盖已有的环境变量
                os.environ[key] = value.strip()


def _get_conn_params() -> dict:
    _load_env_file()
    return {
        'host':     os.environ.get('MYSQL_HOST', '127.0.0.1'),
        'port':     int(os.environ.get('MYSQL_PORT', 3306)),
        'user':     os.environ.get('MYSQL_USER', 'guan'),
        'password': os.environ.get('MYSQL_PASSWORD', 'guan123'),
        'database': os.environ.get('MYSQL_DATABASE', 'guan'),
        'charset':  'utf8mb4',
    }


def _connect() -> pymysql.connections.Connection:
    params = _get_conn_params()
    logger.info("连接 MySQL: %s@%s:%s/%s", params['user'], params['host'], params['port'], params['database'])
    return pymysql.connect(**params)


# ── SQL 工具函数 ───────────────────────────────────────────────────────────────

def _parse_sql_statements(sql_text: str) -> list[str]:
    """从 SQL 文本中解析出有效语句列表（过滤纯注释行和空行）"""
    statements = []
    for chunk in sql_text.split(';'):
        effective_lines = [
            line for line in chunk.splitlines()
            if line.strip() and not line.strip().startswith('--')
        ]
        stmt = '\n'.join(effective_lines).strip()
        if stmt:
            statements.append(stmt)
    return statements


# ── DDL 执行 ───────────────────────────────────────────────────────────────────

def run_ddl(conn: pymysql.connections.Connection):
    """逐条执行 init.sql DDL（幂等，CREATE TABLE IF NOT EXISTS）"""
    logger.info("执行 DDL: %s", DDL_FILE)
    with open(DDL_FILE, encoding='utf-8') as f:
        statements = _parse_sql_statements(f.read())

    with conn.cursor() as cur:
        for stmt in statements:
            cur.execute(stmt)
    conn.commit()
    logger.info("DDL 执行完毕，共 %d 条语句", len(statements))


# 幂等迁移可忽略的 MySQL 错误码
_IDEMPOTENT_ERRORS = {
    1054,  # Unknown column（MODIFY 不存在的列 → 说明 ADD 成功了，MODIFY 是多余的）
    1060,  # Duplicate column name（ADD COLUMN 时列已存在）
    1061,  # Duplicate key name（ADD INDEX 时索引已存在）
    1091,  # Can't DROP; column/key doesn't exist（DROP 不存在的列/索引）
    1146,  # Table doesn't exist（历史迁移改已删除的宽表）
}


def run_migrations(conn: pymysql.connections.Connection):
    """
    幂等执行 sql/migrations/ 下的增量迁移文件（按文件名排序）。
    该目录只放 Docker 时代的增量 SQL，不含旧 schema 的历史迁移文件。
    """
    import glob
    migration_files = sorted(glob.glob(os.path.join(MIGRATION_DIR, '*.sql')))
    if not migration_files:
        logger.info("无增量迁移文件")
        return

    logger.info("执行增量迁移，共 %d 个文件", len(migration_files))
    for sql_file in migration_files:
        logger.info("  迁移文件: %s", os.path.basename(sql_file))
        with open(sql_file, encoding='utf-8') as f:
            statements = _parse_sql_statements(f.read())

        with conn.cursor() as cur:
            for stmt in statements:
                try:
                    cur.execute(stmt)
                    conn.commit()
                except pymysql.err.OperationalError as e:
                    if e.args[0] in _IDEMPOTENT_ERRORS:
                        logger.info("    [跳过] 已存在或不存在（幂等）: %s", e.args[1])
                        conn.rollback()
                    else:
                        raise


# ── Mock 数据构造器 ───────────────────────────────────────────────────────────

def _list_table_ids(conn, table: str) -> list[int]:
    with conn.cursor() as cur:
        cur.execute(f"SELECT `id` FROM `{table}` ORDER BY `id`")
        return [row[0] for row in cur.fetchall()]


def _pick_id(ids: list[int], index: int, default: int = 0) -> int:
    if not ids:
        return default
    return ids[index % len(ids)]


def _insert_if_empty(conn, table: str, rows: list[dict], check_col: str = 'id'):
    """仅当表为空时批量插入；已有数据则返回表中全部 id（幂等）"""
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM `{table}`")
        cnt = cur.fetchone()[0]
        if cnt > 0:
            existing_ids = _list_table_ids(conn, table)
            logger.info("  [跳过] %s 已有 %d 条，复用 ids: %s", table, cnt, existing_ids)
            return existing_ids

        if not rows:
            return []

        cols = list(rows[0].keys())
        placeholders = ', '.join(['%s'] * len(cols))
        col_clause = ', '.join(f'`{c}`' for c in cols)
        sql = f"INSERT INTO `{table}` ({col_clause}) VALUES ({placeholders})"

        values = [tuple(r[c] for c in cols) for r in rows]
        cur.executemany(sql, values)
        conn.commit()

        # pymysql executemany 后 lastrowid 是第一条插入行的 id（MySQL 标准行为）
        first_id = cur.lastrowid
        ids = list(range(first_id, first_id + len(rows)))
        logger.info("  [写入] %s 插入 %d 条，id: %s", table, len(rows), ids)
        return ids


def seed_regions(conn) -> list[int]:
    rows = [
        {'province': '北京市', 'city': '北京市', 'area': '海淀区', 'status': 1},
        {'province': '上海市', 'city': '上海市', 'area': '浦东新区', 'status': 1},
        {'province': '广东省', 'city': '深圳市', 'area': '南山区', 'status': 1},
    ]
    return _insert_if_empty(conn, 'region', rows)


def ensure_regions(conn) -> list[int]:
    """幂等补齐省市区（含天津），供异地演示地址使用"""
    rows = [
        {'province': '北京市', 'city': '北京市', 'area': '海淀区', 'status': 1},
        {'province': '上海市', 'city': '上海市', 'area': '浦东新区', 'status': 1},
        {'province': '广东省', 'city': '深圳市', 'area': '南山区', 'status': 1},
        {'province': '天津市', 'city': '天津市', 'area': '和平区', 'status': 1},
    ]
    inserted = 0
    with conn.cursor() as cur:
        for row in rows:
            cur.execute(
                """
                SELECT `id` FROM `region`
                WHERE `province` = %s AND `city` = %s AND `area` = %s AND `status` = 1
                LIMIT 1
                """,
                (row['province'], row['city'], row['area']),
            )
            if cur.fetchone():
                continue
            cur.execute(
                """
                INSERT INTO `region` (`province`, `city`, `area`, `status`)
                VALUES (%s, %s, %s, %s)
                """,
                (row['province'], row['city'], row['area'], row['status']),
            )
            inserted += 1
    if inserted:
        conn.commit()
        logger.info("  [写入] region 补齐 %d 条", inserted)
    return _list_table_ids(conn, 'region')


def _address_seed_rows(region_ids: list[int]) -> list[dict]:
    region_beijing = _pick_id(region_ids, 0)
    region_shanghai = _pick_id(region_ids, 1)
    return [
        {
            'name': '北京五道口东来顺', 'description': '人均150 / 老北京涮肉',
            'region_id': region_beijing, 'longitude': 116.339, 'latitude': 40.003,
            'img_obj_name': '', 'status': 1,
        },
        {
            'name': '北京三里屯咖啡', 'description': '人均60 / 咖啡约会',
            'region_id': region_beijing, 'longitude': 116.455, 'latitude': 39.937,
            'img_obj_name': '', 'status': 1,
        },
        {
            'name': '北京国子监茶馆', 'description': '人均80 / 茶馆',
            'region_id': region_beijing, 'longitude': 116.417, 'latitude': 39.947,
            'img_obj_name': '', 'status': 1,
        },
        {
            'name': '北京什刹海小馆', 'description': '人均120 / 小馆',
            'region_id': region_beijing, 'longitude': 116.386, 'latitude': 39.941,
            'img_obj_name': '', 'status': 1,
        },
        {
            'name': '北京朝阳公园南门', 'description': '公园散步',
            'region_id': region_beijing, 'longitude': 116.482, 'latitude': 39.933,
            'img_obj_name': '', 'status': 1,
        },
        {
            'name': '上海陆家嘴星巴克', 'description': '人均60 / 咖啡约会',
            'region_id': region_shanghai, 'longitude': 121.499, 'latitude': 31.237,
            'img_obj_name': '', 'status': 1,
        },
    ]


def _tianjin_address_seed_rows(conn, region_ids: list[int]) -> list[dict]:
    region_tianjin = _region_id_by_city(conn, '天津市') or _pick_id(region_ids, 0)
    return [
        {
            'name': '天津滨江道咖啡', 'description': '人均50 / 咖啡约会',
            'region_id': region_tianjin, 'longitude': 117.176, 'latitude': 39.129,
            'img_obj_name': '', 'status': 1,
        },
        {
            'name': '天津意式风情区茶馆', 'description': '人均70 / 茶馆',
            'region_id': region_tianjin, 'longitude': 117.196, 'latitude': 39.134,
            'img_obj_name': '', 'status': 1,
        },
        {
            'name': '天津古文化街小馆', 'description': '人均90 / 小吃',
            'region_id': region_tianjin, 'longitude': 117.188, 'latitude': 39.142,
            'img_obj_name': '', 'status': 1,
        },
        {
            'name': '天津南开大学东门', 'description': '校园散步',
            'region_id': region_tianjin, 'longitude': 117.172, 'latitude': 39.103,
            'img_obj_name': '', 'status': 1,
        },
        {
            'name': '天津之眼河畔', 'description': '河边散步',
            'region_id': region_tianjin, 'longitude': 117.182, 'latitude': 39.154,
            'img_obj_name': '', 'status': 1,
        },
    ]


def _region_id_by_city(conn, city: str) -> int | None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT `id` FROM `region` WHERE `city` = %s AND `status` = 1 ORDER BY `id` LIMIT 1",
            (city,),
        )
        row = cur.fetchone()
    return row[0] if row else None


def _all_address_seed_rows(conn, region_ids: list[int]) -> list[dict]:
    return _address_seed_rows(region_ids) + _tianjin_address_seed_rows(conn, region_ids)


def seed_addresses(conn, region_ids: list[int]) -> list[int]:
    return _insert_if_empty(conn, 'address', _address_seed_rows(region_ids))


def ensure_addresses(conn, region_ids: list[int]) -> list[int]:
    """按 mock 地点名称幂等补齐地址，返回 seed 顺序的 id 列表（供 activity 引用）"""
    rows = _all_address_seed_rows(conn, region_ids)
    ordered_ids = []
    inserted = 0
    with conn.cursor() as cur:
        for row in rows:
            cur.execute(
                "SELECT `id` FROM `address` WHERE `name` = %s AND `status` = 1 LIMIT 1",
                (row['name'],),
            )
            found = cur.fetchone()
            if found:
                ordered_ids.append(found[0])
                continue
            cols = list(row.keys())
            placeholders = ', '.join(['%s'] * len(cols))
            col_clause = ', '.join(f'`{c}`' for c in cols)
            cur.execute(
                f"INSERT INTO `address` ({col_clause}) VALUES ({placeholders})",
                tuple(row[c] for c in cols),
            )
            ordered_ids.append(cur.lastrowid)
            inserted += 1
    if inserted:
        conn.commit()
        logger.info("  [写入] address 补齐 mock 地点 %d 条，ids: %s", inserted, ordered_ids)
    else:
        logger.info("  [跳过] address mock 地点已齐全，ids: %s", ordered_ids)
    return ordered_ids


def seed_passports(conn) -> list[int]:
    rows = [
        {'phone': '13800000001', 'openid': 'mock_openid_md5_001', 'status': 1},
        {'phone': '13800000002', 'openid': 'mock_openid_md5_002', 'status': 1},
        {'phone': '13800000003', 'openid': 'mock_openid_md5_003', 'status': 1},
    ]
    return _insert_if_empty(conn, 'passport', rows)


def seed_profile_attrs(conn, passport_ids: list[int]):
    """mock 资料：一个维度一行。已有记录的账号不覆盖。"""
    specs = [
        (passport_ids[0], (
            ("info", "sex", 1, 0),
            ("info", "birth_year", 1996, 0),
            ("info", "height", 178, 0),
            ("info", "weight", 70, 0),
            ("requirement", "sex", 2, 0),
            ("requirement", "birth_year", 1993, 2003),
            ("requirement", "height", 158, 175),
            ("requirement", "weight", 45, 65),
        )),
        (passport_ids[1], (
            ("info", "sex", 2, 0),
            ("info", "birth_year", 1998, 0),
            ("info", "height", 163, 0),
            ("info", "weight", 52, 0),
            ("requirement", "sex", 1, 0),
            ("requirement", "birth_year", 1990, 2000),
            ("requirement", "height", 170, 190),
            ("requirement", "weight", 60, 90),
        )),
        (passport_ids[2], (
            ("info", "sex", 1, 0),
            ("info", "birth_year", 1995, 0),
            ("info", "height", 175, 0),
            ("info", "weight", 75, 0),
            ("requirement", "sex", 2, 0),
            ("requirement", "birth_year", 1995, 2005),
            ("requirement", "height", 155, 170),
        )),
    ]
    for passport_id, dims in specs:
        if _profile_attr_count(conn, passport_id):
            logger.info("  [跳过] profile_attr 已有数据 passport_id=%s", passport_id)
            continue
        for scope, dim_key, value_min, value_max in dims:
            _upsert_profile_attr(conn, passport_id, scope, dim_key, value_min, value_max)
        logger.info("  [写入] profile_attr passport_id=%s dims=%s", passport_id, len(dims))
    conn.commit()


def _fmt_time(dt: datetime.datetime) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def seed_activities(conn, passport_ids: list[int], address_ids: list[int]) -> list[int]:
    """首页演示：两周内场次 + 双心/实心/心碎常驻场景"""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM `activity`")
        if cur.fetchone()[0] > 0:
            existing_ids = _list_table_ids(conn, 'activity')
            logger.info("  [跳过] activity 已有数据，复用 ids: %s", existing_ids)
            return existing_ids

    if not address_ids:
        logger.warning("  [跳过] activity seed：无可用 address_id")
        return []

    now = datetime.datetime.now()
    p0, p1, p2 = _pick_id(passport_ids, 0), _pick_id(passport_ids, 1), _pick_id(passport_ids, 2)
    aid = lambda i: _pick_id(address_ids, i)
    rows = [
        {
            'address_id': aid(0),
            'start_time': _fmt_time(now + datetime.timedelta(hours=1)),
            'boy_passport_id': 0, 'girl_passport_id': 0,
            'state': 0, 'boy_meet_result': 0, 'girl_meet_result': 0, 'status': 1,
        },
        {
            'address_id': aid(1),
            'start_time': _fmt_time(now + datetime.timedelta(hours=2)),
            'boy_passport_id': 0, 'girl_passport_id': 0,
            'state': 0, 'boy_meet_result': 0, 'girl_meet_result': 0, 'status': 1,
        },
        {
            'address_id': aid(2),
            'start_time': _fmt_time(now + datetime.timedelta(days=2, hours=3)),
            'boy_passport_id': 0, 'girl_passport_id': 0,
            'state': 0, 'boy_meet_result': 0, 'girl_meet_result': 0, 'status': 1,
        },
        {
            'address_id': aid(0),
            'start_time': _fmt_time(now + datetime.timedelta(days=3)),
            'boy_passport_id': p0, 'girl_passport_id': p1,
            'state': 100, 'boy_meet_result': 0, 'girl_meet_result': 0, 'status': 1,
        },
        {
            'address_id': aid(3),
            'start_time': _fmt_time(now + datetime.timedelta(days=5)),
            'boy_passport_id': p0, 'girl_passport_id': 0,
            'state': 1, 'boy_meet_result': 0, 'girl_meet_result': 0, 'status': 1,
        },
        {
            'address_id': aid(1),
            'start_time': _fmt_time(now - datetime.timedelta(days=2)),
            'boy_passport_id': p2, 'girl_passport_id': p1,
            'state': 100, 'boy_meet_result': 1, 'girl_meet_result': 1, 'status': 1,
        },
        {
            'address_id': aid(4),
            'start_time': _fmt_time(now - datetime.timedelta(days=1)),
            'boy_passport_id': p0, 'girl_passport_id': p1,
            'state': 100, 'boy_meet_result': 100, 'girl_meet_result': 0, 'status': 1,
        },
        {
            'address_id': aid(2),
            'start_time': _fmt_time(now + datetime.timedelta(days=10)),
            'boy_passport_id': 0, 'girl_passport_id': 0,
            'state': 0, 'boy_meet_result': 0, 'girl_meet_result': 0, 'status': 1,
        },
        {
            'address_id': aid(3),
            'start_time': _fmt_time(now + datetime.timedelta(minutes=35)),
            'boy_passport_id': 0, 'girl_passport_id': 0,
            'state': 0, 'boy_meet_result': 0, 'girl_meet_result': 0, 'status': 1,
        },
        {
            'address_id': aid(4),
            'start_time': _fmt_time(now + datetime.timedelta(minutes=50)),
            'boy_passport_id': 0, 'girl_passport_id': 0,
            'state': 0, 'boy_meet_result': 0, 'girl_meet_result': 0, 'status': 1,
        },
        {
            'address_id': aid(1),
            'start_time': _fmt_time(now + datetime.timedelta(minutes=75)),
            'boy_passport_id': 0, 'girl_passport_id': 0,
            'state': 0, 'boy_meet_result': 0, 'girl_meet_result': 0, 'status': 1,
        },
        {
            'address_id': aid(0),
            'start_time': _fmt_time(now + datetime.timedelta(minutes=100)),
            'boy_passport_id': 0, 'girl_passport_id': 0,
            'state': 0, 'boy_meet_result': 0, 'girl_meet_result': 0, 'status': 1,
        },
    ]
    return _insert_if_empty(conn, 'activity', rows)


def _address_id_by_name(conn, name: str) -> int | None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT `id` FROM `address` WHERE `name` = %s AND `status` = 1 LIMIT 1",
            (name,),
        )
        row = cur.fetchone()
    return row[0] if row else None


def _upsert_demo_empty_activity(conn, address_id: int, start: datetime.datetime) -> int | None:
    """刷新该地点最近一条空闲场次的开始时间（便于每次 init 后都能在首页看到无心）"""
    start_str = _fmt_time(start)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT `id` FROM `activity`
            WHERE `address_id` = %s AND `state` = 0
              AND `boy_passport_id` = 0 AND `girl_passport_id` = 0 AND `status` = 1
            ORDER BY `start_time` DESC
            LIMIT 1
            """,
            (address_id,),
        )
        row = cur.fetchone()
        if row:
            activity_id = row[0]
            cur.execute(
                "UPDATE `activity` SET `start_time` = %s WHERE `id` = %s",
                (start_str, activity_id),
            )
            return activity_id
        cur.execute(
            """
            INSERT INTO `activity` (
                address_id, start_time, boy_passport_id, girl_passport_id,
                state, boy_meet_result, girl_meet_result, status
            ) VALUES (%s, %s, 0, 0, 0, 0, 0, 1)
            """,
            (address_id, start_str),
        )
        return cur.lastrowid


def ensure_empty_slot_activities(conn, address_ids: list[int]) -> list[int]:
    """补充/刷新空闲（无心）场次：天津演示点 + 北京点，开始时间滚动到未来 1~2 小时内"""
    now = datetime.datetime.now()
    touched_ids = []

    tianjin_slots = [
        ('天津滨江道咖啡', datetime.timedelta(minutes=48)),
        ('天津意式风情区茶馆', datetime.timedelta(minutes=62)),
        ('天津古文化街小馆', datetime.timedelta(minutes=78)),
        ('天津南开大学东门', datetime.timedelta(minutes=95)),
        ('天津之眼河畔', datetime.timedelta(minutes=110)),
    ]
    for name, delta in tianjin_slots:
        address_id = _address_id_by_name(conn, name)
        if not address_id:
            logger.warning("  [跳过] 无心场次：未找到地址 %s", name)
            continue
        activity_id = _upsert_demo_empty_activity(conn, address_id, now + delta)
        if activity_id:
            touched_ids.append(activity_id)

    if address_ids:
        legacy_slots = [
            (_pick_id(address_ids, 2), datetime.timedelta(minutes=40)),
            (_pick_id(address_ids, 3), datetime.timedelta(minutes=65)),
        ]
        for address_id, delta in legacy_slots:
            activity_id = _upsert_demo_empty_activity(conn, address_id, now + delta)
            if activity_id:
                touched_ids.append(activity_id)

    if touched_ids:
        conn.commit()
        logger.info("  [写入] activity 刷新无心场次 %d 条，id: %s", len(touched_ids), touched_ids)
    else:
        logger.info("  [跳过] activity 无心场次未更新")
    return touched_ids


def seed_shares(conn, passport_ids: list[int]) -> list[int]:
    rows = [
        {'share_passport_id': passport_ids[0], 'accept_passport_id': passport_ids[2], 'status': 1},
    ]
    return _insert_if_empty(conn, 'share', rows)


# ── 当前登录用户的可测数据 ─────────────────────────────────────────────────────

MOCK_OPENID_PREFIX = 'mock_openid_md5_'
OPPOSITE_PHONE = '13800000002'
LOGIN_BIRTH_YEAR = 1996
LOGIN_HEIGHT = 178
LOGIN_WEIGHT = 70
STATE_INVITING = 1
STATE_SUCCESS = 100
MEET_RESULT_FIT = 1
MEET_RESULT_UNFIT = 100
MINUTES_PER_DAY = 24 * 60

# 地址名, 相对现在的分钟, 我是否占男方席位, 对方是否占女方席位, state, 男方结果, 女方结果
LOGIN_DEMO_SCENES = (
    ('天津古文化街小馆', 3 * MINUTES_PER_DAY, True, True, STATE_SUCCESS, 0, 0),
    ('天津南开大学东门', -2 * MINUTES_PER_DAY, True, True, STATE_SUCCESS, 0, MEET_RESULT_FIT),
    ('天津之眼河畔', -6 * MINUTES_PER_DAY, True, True, STATE_SUCCESS, MEET_RESULT_UNFIT, 0),
    ('北京三里屯咖啡', 55, False, True, STATE_INVITING, 0, 0),
    ('天津意式风情区茶馆', 70, False, True, STATE_INVITING, 0, 0),
)


def _passport_id_by_sql(conn, sql, params):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
    return row[0] if row else None


def _profile_attr_count(conn, passport_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM `profile_attr` WHERE `passport_id`=%s AND `status`=1",
            (passport_id,),
        )
        return cur.fetchone()[0]


def _upsert_profile_attr(conn, passport_id, scope, dim_key, value_min=0, value_max=0, value_text=""):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO `profile_attr`
                (passport_id, scope, dim_key, value_min, value_max, value_text, status)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
                value_min=VALUES(value_min), value_max=VALUES(value_max),
                value_text=VALUES(value_text), status=1
            """,
            (passport_id, scope, dim_key, value_min, value_max, value_text),
        )


def _sex_value(conn, passport_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT `value_min` FROM `profile_attr`
            WHERE `passport_id`=%s AND `scope`='info' AND `dim_key`='sex' AND `status`=1
            """,
            (passport_id,),
        )
        row = cur.fetchone()
    return row[0] if row else 0


def _fill_login_user_profile(conn, passport_id):
    """只在还没填性别时写入，避免覆盖语音页后来改过的资料。"""
    if _sex_value(conn, passport_id):
        logger.info("  [跳过] 登录用户资料已有性别，不覆盖 passport_id=%s", passport_id)
        return
    dims = (
        ("info", "sex", 1, 0),
        ("info", "birth_year", LOGIN_BIRTH_YEAR, 0),
        ("info", "height", LOGIN_HEIGHT, 0),
        ("info", "weight", LOGIN_WEIGHT, 0),
        ("requirement", "sex", 2, 0),
        ("requirement", "birth_year", 1994, 2001),
        ("requirement", "height", 155, 175),
        ("requirement", "weight", 45, 65),
    )
    for scope, dim_key, value_min, value_max in dims:
        _upsert_profile_attr(conn, passport_id, scope, dim_key, value_min, value_max)
    logger.info("  [写入] 登录用户个人信息和期望 passport_id=%s", passport_id)


def _upsert_login_scene(conn, address_id, boy_id, girl_id, state, boy_result, girl_result, start):
    start_str = _fmt_time(start)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT `id` FROM `activity`
            WHERE `address_id`=%s AND `boy_passport_id`=%s AND `girl_passport_id`=%s AND `status`=1
            ORDER BY `id` DESC LIMIT 1
            """,
            (address_id, boy_id, girl_id),
        )
        row = cur.fetchone()
        if row:
            cur.execute(
                """
                UPDATE `activity` SET
                    start_time=%s, state=%s, boy_meet_result=%s, girl_meet_result=%s
                WHERE id=%s
                """,
                (start_str, state, boy_result, girl_result, row[0]),
            )
            return row[0]
        cur.execute(
            """
            INSERT INTO `activity` (
                address_id, start_time, boy_passport_id, girl_passport_id,
                state, boy_meet_result, girl_meet_result, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
            """,
            (address_id, start_str, boy_id, girl_id, state, boy_result, girl_result),
        )
        return cur.lastrowid


def ensure_login_user_demo(conn) -> list[int]:
    """给最近一个真实登录用户补资料，并挂上各状态见面，便于走通页面。"""
    passport_id = _passport_id_by_sql(
        conn,
        "SELECT `id` FROM `passport` WHERE `status`=1 AND `openid` NOT LIKE %s ORDER BY `id` DESC LIMIT 1",
        (MOCK_OPENID_PREFIX + '%',),
    )
    if not passport_id:
        logger.info("  [跳过] 还没有真实登录用户")
        return []
    opposite_id = _passport_id_by_sql(
        conn,
        "SELECT `id` FROM `passport` WHERE `phone`=%s AND `status`=1 LIMIT 1",
        (OPPOSITE_PHONE,),
    )
    _fill_login_user_profile(conn, passport_id)

    now = datetime.datetime.now()
    activity_ids = []
    for address_name, minutes, boy_is_me, girl_is_opp, state, boy_result, girl_result in LOGIN_DEMO_SCENES:
        address_id = _address_id_by_name(conn, address_name)
        if not address_id or not opposite_id:
            logger.warning("  [跳过] 登录用户场次 %s", address_name)
            continue
        boy_id = passport_id if boy_is_me else 0
        girl_id = opposite_id if girl_is_opp else 0
        activity_id = _upsert_login_scene(
            conn, address_id, boy_id, girl_id, state, boy_result, girl_result,
            now + datetime.timedelta(minutes=minutes),
        )
        if activity_id:
            activity_ids.append(activity_id)
    conn.commit()
    logger.info(
        "  [写入] 登录用户场次 passport_id=%s opposite=%s activity=%s",
        passport_id, opposite_id, activity_ids,
    )
    return activity_ids


# ── 主流程 ─────────────────────────────────────────────────────────────────────

def main():
    conn = _connect()
    try:
        logger.info("=== Step 1: 执行 DDL（幂等）===")
        run_ddl(conn)

        logger.info("=== Step 1.5: 执行增量迁移 ===")
        run_migrations(conn)

        logger.info("=== Step 2: 写入 Mock 数据（幂等）===")
        seed_regions(conn)
        region_ids = ensure_regions(conn)
        seed_addresses(conn, region_ids)
        address_ids   = ensure_addresses(conn, region_ids)
        passport_ids  = seed_passports(conn)
        seed_profile_attrs(conn, passport_ids)
        seed_activities(conn, passport_ids, address_ids)
        ensure_empty_slot_activities(conn, address_ids)
        seed_shares(conn, passport_ids)
        ensure_login_user_demo(conn)

        logger.info("=== 初始化完成 ===")
        _print_summary(conn)
    finally:
        conn.close()


def _print_summary(conn):
    tables = [
        'region', 'address',
        'passport', 'profile_attr', 'activity', 'share',
    ]
    logger.info("─── 数据总览 ───────────────────────────────")
    with conn.cursor() as cur:
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM `{table}`")
            cnt = cur.fetchone()[0]
            logger.info("  %-30s %d 条", table, cnt)
    logger.info("────────────────────────────────────────────")


if __name__ == '__main__':
    main()
