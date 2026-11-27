#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""从 Geofabrik 的 OSM 数据包导入全国肯德基、麦当劳门店。

下载中国 .osm.pbf（约 1.5GB）后在本地筛选，不依赖在线 Overpass，也不要高德 Key。
默认收录全国（含三四五线）；省/市/县优先读 OSM 地址标签，bbox 仅作缺标签时定市。
坐标从 WGS-84 转成国测局 GCJ-02，和小程序定位一致。

用法（在 guan 目录，或容器内 /app）:
  python -m script.osm_store_import --download --dry-run
  python -m script.osm_store_import --download
  python -m script.osm_store_import --pbf /path/to/china-latest.osm.pbf --city 北京市
  python -m script.osm_store_import --city 海淀区
"""
import argparse
import logging
import math
import os
import ssl
import sys
import urllib.request
from collections import Counter, namedtuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import osmium
import pymysql

from script.osm_city_bbox import CITY_BBOX_ROWS
from util.const.match import MODEL_STATUS_YES

logger = logging.getLogger("osm_store_import")

GEOFABRIK_CHINA_PBF_URL = "https://download.geofabrik.de/asia/china-latest.osm.pbf"
DEFAULT_PBF_PATH = os.path.join(SCRIPT_DIR, "data", "china-latest.osm.pbf")
DOWNLOAD_TIMEOUT_SEC = 600
DOWNLOAD_CHUNK_BYTES = 1024 * 1024
DOWNLOAD_LOG_STEP_PERCENT = 5
BYTES_PER_MB = 1024 * 1024
NAME_LIMIT = 256
DESCRIPTION_LIMIT = 512
COORD_DECIMALS = 5
INSERT_BATCH = 200
EXIT_CONFIG = 2
DEFAULT_MYSQL_PORT = 3306
CHINA_LNG_MIN = 73.0
CHINA_LNG_MAX = 136.0
CHINA_LAT_MIN = 3.0
CHINA_LAT_MAX = 54.0
USER_AGENT = "guan-osm-store-import/2.0"
EXCLUDE_NAME_PARTS = ("宅急送", "外卖", "配送", "配送站")
FALLBACK_PROVINCE = "未标注"
FALLBACK_CITY = "未标注"

KRASOVSKY_A = 6378245.0
EE = 0.00669342162296594323
GCJ_OFFSET_LNG = 105.0
GCJ_OFFSET_LAT = 35.0

Brand = namedtuple("Brand", "keyword image wikidata aliases")
City = namedtuple("City", "name province south west north east")
Store = namedtuple(
    "Store", "name description province city area longitude latitude image"
)

BRANDS = (
    Brand("肯德基", "address/brand/kfc.png", "Q177054", ("kfc",)),
    Brand("麦当劳", "address/brand/mcdonalds.jpg", "Q38076", ("mcdonald",)),
)

def _cities_from_rows(rows):
    seen = set()
    cities = []
    for row in rows:
        name = row[0]
        if name in seen:
            continue
        seen.add(name)
        cities.append(City(*row))
    return tuple(cities)


CITY_BBOXES = _cities_from_rows(CITY_BBOX_ROWS)
TIER1_NEW_TIER1_NAMES = frozenset((
    "北京市", "上海市", "广州市", "深圳市", "成都市", "重庆市", "杭州市",
    "西安市", "武汉市", "苏州市", "郑州市", "南京市", "天津市", "长沙市",
    "东莞市", "宁波市", "佛山市", "合肥市", "青岛市",
))
MAJOR_CITIES = tuple(
    city for city in CITY_BBOXES if city.name in TIER1_NEW_TIER1_NAMES
)

INSERT_ADDRESS_SQL = """
INSERT INTO address (name, description, region_id, longitude, latitude, img_obj_name, status)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""
INSERT_REGION_SQL = """
INSERT INTO region (province, city, area, status) VALUES (%s, %s, %s, %s)
"""


def clip(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit]


def plain_text(value):
    if value is None or isinstance(value, (list, dict)):
        return ""
    return str(value).strip()


def out_of_china(longitude, latitude):
    return not (
        CHINA_LNG_MIN <= longitude <= CHINA_LNG_MAX
        and CHINA_LAT_MIN <= latitude <= CHINA_LAT_MAX
    )


def _transform_lat(x, y):
    result = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    result += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    result += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
    result += (160.0 * math.sin(y / 12.0 * math.pi) + 320.0 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
    return result


def _transform_lng(x, y):
    result = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    result += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    result += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
    result += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
    return result


def wgs84_to_gcj02(longitude, latitude):
    if out_of_china(longitude, latitude):
        return longitude, latitude
    dlat = _transform_lat(longitude - GCJ_OFFSET_LNG, latitude - GCJ_OFFSET_LAT)
    dlng = _transform_lng(longitude - GCJ_OFFSET_LNG, latitude - GCJ_OFFSET_LAT)
    rad_lat = latitude / 180.0 * math.pi
    sin_lat = math.sin(rad_lat)
    magic = 1 - EE * sin_lat * sin_lat
    sqrt_magic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((KRASOVSKY_A * (1 - EE)) / (magic * sqrt_magic) * math.pi)
    dlng = (dlng * 180.0) / (KRASOVSKY_A / sqrt_magic * math.cos(rad_lat) * math.pi)
    return longitude + dlng, latitude + dlat


def store_identity(name, longitude, latitude):
    return (name, round(float(longitude), COORD_DECIMALS), round(float(latitude), COORD_DECIMALS))


def tags_to_dict(tags):
    return {tag.k: tag.v for tag in tags}


def brand_of_tags(tags):
    tags = tags or {}
    wikidata = plain_text(tags.get("brand:wikidata"))
    for brand in BRANDS:
        if wikidata == brand.wikidata:
            return brand
    blob = " ".join(
        plain_text(tags.get(key))
        for key in ("name", "name:zh", "brand", "brand:zh", "brand:en")
    )
    lowered = blob.lower()
    for brand in BRANDS:
        if brand.keyword in blob:
            return brand
        if any(alias in lowered for alias in brand.aliases):
            return brand
    return None


def admin_stem(name):
    text = name or ""
    for suffix in ("自治州", "地区", "盟", "市", "县", "区"):
        if text.endswith(suffix):
            return text[:-len(suffix)]
    return text


def place_selected(store, names):
    if not names:
        return True
    city_stem = admin_stem(store.city)
    area = store.area or ""
    area_stem = admin_stem(area)
    for name in names:
        stem = admin_stem(name)
        if store.city == name or city_stem == stem:
            return True
        if area and (area == name or area_stem == stem):
            return True
    return False


def city_containing(longitude, latitude, cities):
    for city in cities:
        if city.south <= latitude <= city.north and city.west <= longitude <= city.east:
            return city
    return None


def first_tag(tags, keys):
    for key in keys:
        value = plain_text(tags.get(key))
        if value:
            return value
    return ""


def admin_from_tags(tags):
    province = first_tag(tags, ("addr:province", "is_in:province", "is_in:state"))
    city = first_tag(tags, ("addr:city", "addr:municipality", "is_in:city"))
    area = first_tag(
        tags,
        (
            "addr:county",
            "addr:district",
            "addr:city_district",
            "addr:suburb",
            "addr:town",
            "addr:village",
        ),
    )
    return province, city, area


def resolve_admin(tags, wgs_lng, wgs_lat, cities):
    province, city, area = admin_from_tags(tags)
    matched = city_containing(wgs_lng, wgs_lat, cities) if cities else None
    if matched:
        return matched.province, matched.name, area
    if not city and province:
        city = province
    if not province and city:
        province = city
    if not province or not city:
        return FALLBACK_PROVINCE, FALLBACK_CITY, area
    return province, city, area


def store_from_wgs(tags, wgs_lng, wgs_lat, cities=CITY_BBOXES):
    brand = brand_of_tags(tags)
    if brand is None:
        return None
    name = clip(plain_text(tags.get("name") or tags.get("name:zh") or brand.keyword), NAME_LIMIT)
    if any(part in name for part in EXCLUDE_NAME_PARTS):
        return None
    if out_of_china(wgs_lng, wgs_lat):
        return None
    longitude, latitude = wgs84_to_gcj02(wgs_lng, wgs_lat)
    province, city, area = resolve_admin(tags, wgs_lng, wgs_lat, cities)
    address = plain_text(tags.get("addr:full") or tags.get("addr:street"))
    description = address or " ".join(part for part in (province, city, area) if part)
    return Store(
        name,
        clip(description, DESCRIPTION_LIMIT),
        province,
        city,
        area,
        longitude,
        latitude,
        brand.image,
    )


def dedup_stores(stores, existing=()):
    seen = set(existing)
    fresh = []
    for store in stores:
        if store is None:
            continue
        key = store_identity(store.name, store.longitude, store.latitude)
        if key in seen:
            continue
        seen.add(key)
        fresh.append(store)
    return fresh


def address_values(store, region_id):
    return (
        store.name,
        store.description,
        region_id or 0,
        store.longitude,
        store.latitude,
        store.image,
        MODEL_STATUS_YES,
    )


class BrandHandler(osmium.SimpleHandler):
    """只扫 node 上的肯德基/麦当劳（WGS-84）；不开 locations 索引，避免全国包 OOM。"""

    def __init__(self):
        super(BrandHandler, self).__init__()
        self.points = []

    def node(self, node):
        if not node.location.valid():
            return
        if brand_of_tags(node.tags) is None:
            return
        self.points.append(
            (tags_to_dict(node.tags), node.location.lon, node.location.lat)
        )


def collect_brand_points(pbf_path):
    handler = BrandHandler()
    logger.info("开始扫描 PBF path=%s mode=node-only", pbf_path)
    handler.apply_file(pbf_path, locations=False)
    logger.info("扫描完成 brand_points=%s", len(handler.points))
    return handler.points


def stores_from_points(points, cities=CITY_BBOXES, place_names=None):
    stores = []
    for tags, wgs_lng, wgs_lat in points:
        store = store_from_wgs(tags, wgs_lng, wgs_lat, cities)
        if not store:
            continue
        if place_names and not place_selected(store, place_names):
            continue
        stores.append(store)
    return dedup_stores(stores)


def load_env_file():
    env_path = os.path.join(PROJECT_ROOT, ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if key not in os.environ:
                os.environ[key] = value.strip()


def download_pbf(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + ".part"
    logger.info("开始下载 url=%s -> %s", url, path)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(
        request, timeout=DOWNLOAD_TIMEOUT_SEC, context=ssl.create_default_context(),
    ) as response:
        total = int(response.headers.get("Content-Length") or 0)
        read_bytes = 0
        last_logged = -DOWNLOAD_LOG_STEP_PERCENT
        with open(temporary, "wb") as out:
            while True:
                chunk = response.read(DOWNLOAD_CHUNK_BYTES)
                if not chunk:
                    break
                out.write(chunk)
                read_bytes += len(chunk)
                if total <= 0:
                    continue
                percent = int(read_bytes * 100 / total)
                if percent >= last_logged + DOWNLOAD_LOG_STEP_PERCENT:
                    logger.info(
                        "下载进度 %s%% (%s/%s MB)",
                        percent,
                        read_bytes // BYTES_PER_MB,
                        total // BYTES_PER_MB,
                    )
                    last_logged = percent
    os.replace(temporary, path)
    logger.info("下载完成 path=%s size_mb=%s", path, os.path.getsize(path) // BYTES_PER_MB)
    return path


class AddressWriter(object):
    def __init__(self, conn):
        self.conn = conn
        self.regions = {}
        self.keys = set()
        self._load()

    @classmethod
    def connect(cls):
        load_env_file()
        conn = pymysql.connect(
            host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
            port=int(os.environ.get("MYSQL_PORT", str(DEFAULT_MYSQL_PORT))),
            user=os.environ.get("MYSQL_USER", "guan"),
            password=os.environ.get("MYSQL_PASSWORD", "guan123"),
            database=os.environ.get("MYSQL_DATABASE", "guan"),
            charset="utf8mb4",
            autocommit=False,
        )
        return cls(conn)

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def _load(self):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, province, city, area FROM region WHERE status = %s",
                (MODEL_STATUS_YES,),
            )
            for region_id, province, city, area in cur.fetchall():
                self.regions.setdefault((province, city, area), region_id)
            cur.execute(
                "SELECT name, longitude, latitude FROM address WHERE status = %s",
                (MODEL_STATUS_YES,),
            )
            for name, longitude, latitude in cur.fetchall():
                self.keys.add(store_identity(name, longitude, latitude))

    def insert_stores(self, stores):
        fresh = dedup_stores(stores, self.keys)
        if not fresh:
            return 0
        missing = self._missing_regions(fresh)
        with self.conn.cursor() as cur:
            if missing:
                cur.executemany(
                    INSERT_REGION_SQL,
                    [(province, city, area, MODEL_STATUS_YES) for province, city, area in missing],
                )
                self._remember_regions(cur, missing)
            for start in range(0, len(fresh), INSERT_BATCH):
                batch = fresh[start:start + INSERT_BATCH]
                cur.executemany(INSERT_ADDRESS_SQL, [self._row(store) for store in batch])
        self.conn.commit()
        for store in fresh:
            self.keys.add(store_identity(store.name, store.longitude, store.latitude))
        return len(fresh)

    def _missing_regions(self, stores):
        missing = []
        seen = set()
        for store in stores:
            triple = self._region_key(store)
            if triple is None or triple in self.regions or triple in seen:
                continue
            seen.add(triple)
            missing.append(triple)
        return missing

    def _region_key(self, store):
        if not store.province or not store.city:
            return None
        return (store.province, store.city, store.area or "")

    def _row(self, store):
        return address_values(store, self.regions.get(self._region_key(store), 0))

    def _remember_regions(self, cur, missing):
        if not missing:
            return
        holders = ", ".join(["(%s, %s, %s)"] * len(missing))
        params = [MODEL_STATUS_YES]
        for province, city, area in missing:
            params.extend((province, city, area))
        cur.execute(
            "SELECT id, province, city, area FROM region "
            "WHERE status = %s AND (province, city, area) IN (" + holders + ")",
            params,
        )
        for region_id, province, city, area in cur.fetchall():
            self.regions.setdefault((province, city, area), region_id)


def parse_args(argv):
    parser = argparse.ArgumentParser(description="从 OSM PBF 导入全国肯德基、麦当劳门店")
    parser.add_argument("--pbf", default="", help="本地 .osm.pbf 路径，默认 script/data/china-latest.osm.pbf")
    parser.add_argument("--download", action="store_true", help="从 Geofabrik 下载中国数据包")
    parser.add_argument(
        "--city",
        action="append",
        default=[],
        help="只保留指定市或县/区，可重复。默认全国",
    )
    parser.add_argument("--dry-run", action="store_true", help="只统计数量，不写数据库")
    return parser.parse_args(argv)


def resolve_pbf_path(args):
    path = args.pbf.strip() or DEFAULT_PBF_PATH
    if os.path.exists(path):
        if args.download:
            logger.info("PBF 已存在，跳过下载 path=%s", path)
        return path
    if not args.download:
        logger.error("找不到 PBF：%s 。请加 --download，或用 --pbf 指定已下载文件", path)
        return ""
    download_pbf(GEOFABRIK_CHINA_PBF_URL, path)
    return path


def run_import(pbf_path, writer, cities=CITY_BBOXES, place_names=None):
    points = collect_brand_points(pbf_path)
    stores = stores_from_points(points, cities, place_names=place_names)
    for city_name, count in sorted(Counter(store.city for store in stores).items()):
        logger.info("city=%s stores=%s", city_name, count)
    with_area = sum(1 for store in stores if store.area)
    logger.info(
        "行政区划 area有值=%s area空=%s fallback市=%s",
        with_area,
        len(stores) - with_area,
        sum(1 for store in stores if store.city == FALLBACK_CITY),
    )
    if writer is None:
        logger.info("dry-run 合计 stores=%s", len(stores))
        return len(stores)
    inserted = writer.insert_stores(stores)
    logger.info("入库完成 fetched=%s inserted=%s", len(stores), inserted)
    return inserted


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = parse_args(sys.argv[1:] if argv is None else argv)
    pbf_path = resolve_pbf_path(args)
    if not pbf_path:
        return EXIT_CONFIG
    place_names = args.city or None
    brand_names = "、".join(brand.keyword for brand in BRANDS)
    scope = "、".join(args.city) if args.city else "全国"
    logger.info(
        "准备导入 scope=%s bbox城市=%s brands=%s pbf=%s",
        scope,
        len(CITY_BBOXES),
        brand_names,
        pbf_path,
    )
    if args.dry_run:
        count = run_import(pbf_path, None, CITY_BBOXES, place_names=place_names)
    else:
        with AddressWriter.connect() as writer:
            count = run_import(pbf_path, writer, CITY_BBOXES, place_names=place_names)
    if place_names and count == 0:
        logger.error("按市/县过滤后无门店：%s", "、".join(args.city))
        return EXIT_CONFIG
    return 0


if __name__ == "__main__":
    sys.exit(main())
