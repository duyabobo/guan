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

def _insert_if_empty(conn, table: str, rows: list[dict], check_col: str = 'id'):
    """仅当表为空时批量插入；已有数据则查库返回已有的前 N 条 id（幂等）"""
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM `{table}`")
        cnt = cur.fetchone()[0]
        if cnt > 0:
            cur.execute(f"SELECT `id` FROM `{table}` ORDER BY `id` LIMIT %s", (len(rows),))
            existing_ids = [row[0] for row in cur.fetchall()]
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


def seed_educations(conn) -> list[int]:
    rows = [
        {'category': '工学',   'disciplines': '计算机类', 'major': '软件工程', 'seq': 1, 'status': 1},
        {'category': '管理学', 'disciplines': '工商管理类', 'major': '市场营销', 'seq': 2, 'status': 1},
        {'category': '理学',   'disciplines': '数学类', 'major': '应用数学', 'seq': 3, 'status': 1},
    ]
    return _insert_if_empty(conn, 'education', rows)


def seed_works(conn) -> list[int]:
    rows = [
        {'profession': '互联网', 'industry': '后端开发', 'position': '工程师', 'seq': 1, 'status': 1},
        {'profession': '金融',   'industry': '投资',     'position': '分析师', 'seq': 2, 'status': 1},
        {'profession': '教育',   'industry': '在线教育', 'position': '产品经理', 'seq': 3, 'status': 1},
    ]
    return _insert_if_empty(conn, 'work', rows)


def seed_schools(conn, region_ids: list[int]) -> list[int]:
    rows = [
        {'region_id': region_ids[0], 'name': '北京大学',   'logo': '', 'nature_name': '公办', 'school_type_name': '本科', 'seq': 1, 'status': 1},
        {'region_id': region_ids[1], 'name': '复旦大学',   'logo': '', 'nature_name': '公办', 'school_type_name': '本科', 'seq': 2, 'status': 1},
        {'region_id': region_ids[2], 'name': '深圳大学',   'logo': '', 'nature_name': '公办', 'school_type_name': '本科', 'seq': 3, 'status': 1},
    ]
    return _insert_if_empty(conn, 'school', rows)


def seed_addresses(conn, region_ids: list[int]) -> list[int]:
    rows = [
        {
            'name': '北京五道口东来顺', 'description': '人均150 / 老北京涮肉',
            'region_id': region_ids[0], 'longitude': 116.339, 'latitude': 40.003,
            'img_obj_name': '', 'status': 1,
        },
        {
            'name': '上海陆家嘴星巴克', 'description': '人均60 / 咖啡约会',
            'region_id': region_ids[1], 'longitude': 121.499, 'latitude': 31.237,
            'img_obj_name': '', 'status': 1,
        },
    ]
    return _insert_if_empty(conn, 'address', rows)


def seed_passports(conn) -> list[int]:
    rows = [
        {'phone': '13800000001', 'openid': 'mock_openid_md5_001', 'status': 1},
        {'phone': '13800000002', 'openid': 'mock_openid_md5_002', 'status': 1},
        {'phone': '13800000003', 'openid': 'mock_openid_md5_003', 'status': 1},
    ]
    return _insert_if_empty(conn, 'passport', rows)


def seed_users(conn, passport_ids: list[int], region_ids: list[int],
               education_ids: list[int], work_ids: list[int],
               school_ids: list[int]) -> list[int]:
    """
    mock 3 个用户: 男/女/男
    sex: 1=男, 2=女  |  martial_status: 1=未婚
    verify_type: 1=学校认证, 2=工作认证, 0=无认证
    """
    rows = [
        {  # 用户1：男，学校认证，信息已完善
            'passport_id': passport_ids[0], 'allow_location': 1,
            'sex': 1, 'verify_type': 1, 'has_head_img': 1, 'head_img_version': 1,
            'birth_year': 1996, 'height': 178, 'weight': 70,
            'home_region_id': region_ids[0],
            'study_from_year': 2015, 'study_region_id': region_ids[0],
            'school_id': school_ids[0], 'education_level': 2, 'education_id': education_ids[0],
            'work_region_id': region_ids[0], 'work_id': work_ids[0], 'month_pay': 25000,
            'martial_status': 1, 'info_has_filled': 1, 'status': 1,
        },
        {  # 用户2：女，工作认证，信息已完善
            'passport_id': passport_ids[1], 'allow_location': 1,
            'sex': 2, 'verify_type': 2, 'has_head_img': 1, 'head_img_version': 1,
            'birth_year': 1998, 'height': 163, 'weight': 52,
            'home_region_id': region_ids[1],
            'study_from_year': 2017, 'study_region_id': region_ids[1],
            'school_id': school_ids[1], 'education_level': 2, 'education_id': education_ids[1],
            'work_region_id': region_ids[1], 'work_id': work_ids[1], 'month_pay': 18000,
            'martial_status': 1, 'info_has_filled': 1, 'status': 1,
        },
        {  # 用户3：男，无认证，信息未完善
            'passport_id': passport_ids[2], 'allow_location': 0,
            'sex': 1, 'verify_type': 0, 'has_head_img': -1, 'head_img_version': 0,
            'birth_year': 1995, 'height': 175, 'weight': 75,
            'home_region_id': region_ids[2],
            'study_from_year': 2014, 'study_region_id': region_ids[2],
            'school_id': school_ids[2], 'education_level': 2, 'education_id': education_ids[2],
            'work_region_id': region_ids[2], 'work_id': work_ids[2], 'month_pay': 12000,
            'martial_status': 1, 'info_has_filled': 0, 'status': 1,
        },
    ]
    return _insert_if_empty(conn, 'user', rows)


def seed_requirements(conn, passport_ids: list[int]) -> list[int]:
    """期望条件：用户1找女性，用户2找男性，用户3找女性（仅填核心条件，其余 0=不限）"""
    _ZERO_REGION = {'home_region_id': 0, 'study_region_id': 0, 'work_region_id': 0}
    _ZERO_EDU    = {'school_id': 0, 'work_id': 0, 'education_id': 0,
                    'education_level': 0, 'min_study_from_year': 0, 'max_study_from_year': 0}
    rows = [
        {
            'passport_id': passport_ids[0], 'verify_type': 0,
            'sex': 2, 'martial_status': 2,
            'min_birth_year': 1993, 'max_birth_year': 2003,
            'min_height': 158, 'max_height': 175,
            'min_weight': 45, 'max_weight': 65,
            'min_month_pay': 0, 'max_month_pay': 0,
            **_ZERO_REGION, **_ZERO_EDU, 'status': 1,
        },
        {
            'passport_id': passport_ids[1], 'verify_type': 0,
            'sex': 1, 'martial_status': 1,
            'min_birth_year': 1990, 'max_birth_year': 2000,
            'min_height': 170, 'max_height': 190,
            'min_weight': 60, 'max_weight': 90,
            'min_month_pay': 15000, 'max_month_pay': 0,
            **_ZERO_REGION, **_ZERO_EDU, 'status': 1,
        },
        {
            'passport_id': passport_ids[2], 'verify_type': 0,
            'sex': 2, 'martial_status': 0,
            'min_birth_year': 1995, 'max_birth_year': 2005,
            'min_height': 155, 'max_height': 170,
            'min_weight': 0, 'max_weight': 0,
            'min_month_pay': 0, 'max_month_pay': 0,
            **_ZERO_REGION, **_ZERO_EDU, 'status': 1,
        },
    ]
    return _insert_if_empty(conn, 'requirement', rows)


def seed_verifies(conn, passport_ids: list[int]) -> list[int]:
    """认证信息：用户1/2已认证，用户3未认证"""
    rows = [
        {'passport_id': passport_ids[0], 'mail': 'encrypted_pku_mail', 'mail_type': 1, 'mail_verify_status': 1, 'status': 1},
        {'passport_id': passport_ids[1], 'mail': 'encrypted_work_mail', 'mail_type': 2, 'mail_verify_status': 1, 'status': 1},
        {'passport_id': passport_ids[2], 'mail': '', 'mail_type': 0, 'mail_verify_status': 0, 'status': 1},
    ]
    return _insert_if_empty(conn, 'verify', rows)


def seed_activities(conn, passport_ids: list[int], address_ids: list[int]) -> list[int]:
    """
    3 个活动场景:
      1. 空闲活动（无人参与）
      2. 邀请成功，见面时间在未来（等待见面）
      3. 邀请成功，见面已过去，双方都选了合适（已成功）
    """
    now = datetime.datetime.now()
    rows = [
        {  # 空闲活动
            'address_id': address_ids[0],
            'start_time': (now + datetime.timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
            'boy_passport_id': 0, 'girl_passport_id': 0,
            'state': 0, 'boy_meet_result': 0, 'girl_meet_result': 0, 'status': 1,
        },
        {  # 用户1(男)邀请用户2(女)，见面时间在3天后
            'address_id': address_ids[0],
            'start_time': (now + datetime.timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'boy_passport_id': passport_ids[0], 'girl_passport_id': passport_ids[1],
            'state': 100, 'boy_meet_result': 0, 'girl_meet_result': 0, 'status': 1,
        },
        {  # 已见面，双方都选了合适
            'address_id': address_ids[1],
            'start_time': (now - datetime.timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'boy_passport_id': passport_ids[2], 'girl_passport_id': passport_ids[1],
            'state': 100, 'boy_meet_result': 1, 'girl_meet_result': 1, 'status': 1,
        },
    ]
    return _insert_if_empty(conn, 'activity', rows)


def seed_shares(conn, passport_ids: list[int]) -> list[int]:
    rows = [
        {'share_passport_id': passport_ids[0], 'accept_passport_id': passport_ids[2], 'status': 1},
    ]
    return _insert_if_empty(conn, 'share', rows)


# ── 主流程 ─────────────────────────────────────────────────────────────────────

def main():
    conn = _connect()
    try:
        logger.info("=== Step 1: 执行 DDL（幂等）===")
        run_ddl(conn)

        logger.info("=== Step 1.5: 执行增量迁移 ===")
        run_migrations(conn)

        logger.info("=== Step 2: 写入 Mock 数据（幂等）===")
        region_ids    = seed_regions(conn)
        education_ids = seed_educations(conn)
        work_ids      = seed_works(conn)
        school_ids    = seed_schools(conn, region_ids)
        address_ids   = seed_addresses(conn, region_ids)
        passport_ids  = seed_passports(conn)
        seed_users(conn, passport_ids, region_ids, education_ids, work_ids, school_ids)
        seed_requirements(conn, passport_ids)
        seed_verifies(conn, passport_ids)
        seed_activities(conn, passport_ids, address_ids)
        seed_shares(conn, passport_ids)

        logger.info("=== 初始化完成 ===")
        _print_summary(conn)
    finally:
        conn.close()


def _print_summary(conn):
    tables = [
        'region', 'education', 'work', 'school', 'address',
        'passport', 'user', 'requirement', 'verify', 'activity', 'share',
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
