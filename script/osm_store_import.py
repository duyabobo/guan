#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""从 OpenStreetMap 一次性导入各大城市肯德基、麦当劳门店。

数据来自 Overpass API，免费、无需 Key。OSM 坐标是 WGS-84，写入前转成
国测局 GCJ-02，和小程序定位一致。国内 OSM 覆盖不如商业地图全，漏店可接受。

用法（在 guan 目录，或容器内 /app）:
  python -m script.osm_store_import --dry-run
  python -m script.osm_store_import --city 北京市
  python -m script.osm_store_import
"""
import argparse
import json
import logging
import math
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request
from collections import namedtuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pymysql

from util.const.match import MODEL_STATUS_YES

logger = logging.getLogger("osm_store_import")

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HTTP_TIMEOUT_SEC = 180
OVERPASS_QUERY_TIMEOUT_SEC = 120
REQUEST_INTERVAL_SEC = 2.0
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
USER_AGENT = "guan-osm-store-import/1.0"
PROGRESS_PATH = os.path.join(SCRIPT_DIR, "data", "osm_store_progress.json")
EXCLUDE_NAME_PARTS = ("宅急送", "外卖", "配送", "配送站")

# 克拉索夫斯基椭球参数，WGS-84 → GCJ-02 纠偏用
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

# 一线 + 新一线。bbox 为 (south, west, north, east)，略放大以免漏边界店。
MAJOR_CITIES = (
    City("北京市", "北京市", 39.40, 115.70, 41.10, 117.50),
    City("上海市", "上海市", 30.65, 120.80, 31.90, 122.20),
    City("广州市", "广东省", 22.75, 113.05, 23.60, 113.80),
    City("深圳市", "广东省", 22.40, 113.75, 22.90, 114.65),
    City("成都市", "四川省", 30.30, 103.70, 31.05, 104.55),
    City("重庆市", "重庆市", 29.00, 105.90, 30.20, 107.20),
    City("杭州市", "浙江省", 29.95, 119.70, 30.60, 120.70),
    City("西安市", "陕西省", 34.00, 108.65, 34.55, 109.30),
    City("武汉市", "湖北省", 30.30, 114.00, 30.90, 114.70),
    City("苏州市", "江苏省", 31.00, 120.20, 31.60, 121.10),
    City("郑州市", "河南省", 34.50, 113.30, 34.95, 113.95),
    City("南京市", "江苏省", 31.80, 118.50, 32.30, 119.10),
    City("天津市", "天津市", 38.75, 116.70, 39.50, 118.10),
    City("长沙市", "湖南省", 27.90, 112.70, 28.45, 113.40),
    City("东莞市", "广东省", 22.70, 113.50, 23.20, 114.20),
    City("宁波市", "浙江省", 29.60, 121.20, 30.10, 121.95),
    City("佛山市", "广东省", 22.80, 112.80, 23.30, 113.40),
    City("合肥市", "安徽省", 31.60, 117.00, 32.05, 117.60),
    City("青岛市", "山东省", 35.90, 119.90, 36.50, 120.70),
)

INSERT_ADDRESS_SQL = """
INSERT INTO address (name, description, region_id, longitude, latitude, img_obj_name, status)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""
INSERT_REGION_SQL = """
INSERT INTO region (province, city, area, status) VALUES (%s, %s, %s, %s)
"""


class OverpassError(Exception):
    pass


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
    """把 OSM 的 WGS-84 转成国测局 GCJ-02。"""
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


def element_point(element):
    if "lat" in element and "lon" in element:
        return float(element["lon"]), float(element["lat"])
    center = element.get("center") or {}
    if "lat" in center and "lon" in center:
        return float(center["lon"]), float(center["lat"])
    return None


def store_from_element(element, city):
    tags = element.get("tags") or {}
    brand = brand_of_tags(tags)
    if brand is None:
        return None
    name = clip(plain_text(tags.get("name") or tags.get("name:zh") or brand.keyword), NAME_LIMIT)
    if any(part in name for part in EXCLUDE_NAME_PARTS):
        return None
    point = element_point(element)
    if not point:
        return None
    wgs_lng, wgs_lat = point
    if out_of_china(wgs_lng, wgs_lat):
        return None
    longitude, latitude = wgs84_to_gcj02(wgs_lng, wgs_lat)
    area = plain_text(
        tags.get("addr:district")
        or tags.get("addr:suburb")
        or tags.get("addr:city_district")
    )
    address = plain_text(tags.get("addr:full") or tags.get("addr:street"))
    description = address or " ".join(
        part for part in (city.province, city.name, area) if part
    )
    return Store(
        name,
        clip(description, DESCRIPTION_LIMIT),
        city.province,
        city.name,
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


def overpass_query(city):
    bbox = "%s,%s,%s,%s" % (city.south, city.west, city.north, city.east)
    parts = []
    for brand in BRANDS:
        parts.append('  nwr["brand:wikidata"="%s"](%s);' % (brand.wikidata, bbox))
        parts.append('  nwr["name"~"%s"](%s);' % (brand.keyword, bbox))
        parts.append('  nwr["brand"~"%s"](%s);' % (brand.keyword, bbox))
    return "\n".join([
        "[out:json][timeout:%s];" % OVERPASS_QUERY_TIMEOUT_SEC,
        "(",
        *parts,
        ");",
        "out center tags;",
    ])


def city_selected(city, names):
    if not names:
        return True
    city_stem = city.name.rstrip("市")
    for name in names:
        name_stem = name.rstrip("市")
        if city.name == name or city_stem == name_stem:
            return True
    return False


def load_done(path):
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as progress_file:
        data = json.load(progress_file)
    return set(data.get("done") or [])


def save_done(path, done):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as progress_file:
        json.dump({"done": sorted(done)}, progress_file, ensure_ascii=False)
    os.replace(temporary, path)


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


def http_post_json(url, body):
    encoded = urllib.parse.urlencode({"data": body}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=encoded,
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        },
        method="POST",
    )
    with urllib.request.urlopen(
        request, timeout=HTTP_TIMEOUT_SEC, context=ssl.create_default_context(),
    ) as response:
        return json.loads(response.read().decode("utf-8"))


class OverpassClient(object):
    def __init__(self, post_json, pause):
        self.post_json = post_json
        self.pause = pause

    def fetch_city(self, city):
        self.pause()
        payload = self.post_json(OVERPASS_URL, overpass_query(city))
        if not isinstance(payload, dict):
            raise OverpassError("响应不是 JSON 对象 city=%s" % city.name)
        elements = payload.get("elements") or []
        if not isinstance(elements, list):
            return []
        stores = []
        for element in elements:
            store = store_from_element(element, city)
            if store:
                stores.append(store)
        return dedup_stores(stores)


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
            triple = (store.province, store.city, store.area)
            if not all(triple) or triple in self.regions or triple in seen:
                continue
            seen.add(triple)
            missing.append(triple)
        return missing

    def _row(self, store):
        return address_values(store, self.regions.get((store.province, store.city, store.area), 0))

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
    parser = argparse.ArgumentParser(description="从 OSM 导入各大城市肯德基、麦当劳门店")
    parser.add_argument("--city", action="append", default=[], help="城市名，可重复。默认一线+新一线")
    parser.add_argument("--dry-run", action="store_true", help="只查询并打印数量，不写数据库")
    return parser.parse_args(argv)


def run_import(client, writer, cities, done, record_done):
    inserted_total = 0
    for city in cities:
        if city.name in done:
            logger.info("已完成，跳过 city=%s", city.name)
            continue
        stores = client.fetch_city(city)
        if writer is None:
            inserted = len(stores)
        else:
            inserted = writer.insert_stores(stores)
        inserted_total += inserted
        logger.info(
            "city=%s fetched=%s inserted=%s",
            city.name, len(stores), inserted,
        )
        if record_done:
            done.add(city.name)
            save_done(PROGRESS_PATH, done)
    return inserted_total


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = parse_args(sys.argv[1:] if argv is None else argv)
    cities = [city for city in MAJOR_CITIES if city_selected(city, args.city)]
    if args.city and not cities:
        logger.error("城市不在内置名单里：%s", "、".join(args.city))
        return EXIT_CONFIG
    brand_names = "、".join(brand.keyword for brand in BRANDS)
    logger.info("准备导入 cities=%s brands=%s", len(cities), brand_names)
    client = OverpassClient(http_post_json, lambda: time.sleep(REQUEST_INTERVAL_SEC))
    if args.dry_run:
        run_import(client, None, cities, set(), False)
        return 0
    done = load_done(PROGRESS_PATH)
    with AddressWriter.connect() as writer:
        run_import(client, writer, cities, done, True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
