#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""按城市把连锁餐饮门店写入 address。

地点来自高德 Web 服务关键字搜索：
https://restapi.amap.com/v5/place/text
同一组参数最多返回 200 条。一个城市到顶后，再按该市的区县 adcode 查。
坐标是国测局 GCJ-02，和小程序定位一致。

图片是各品牌同一张，已放在七牛 address/brand/ 下。杨国福、半天妖、巫山烤鱼
没有核对到可公开访问的官方图，图片先留空。

用法（在 guan 目录）:
  python -m script.brand_store_import --city 北京市 --brand 东来顺 --limit 5
  python -m script.brand_store_import
"""
import argparse
import json
import logging
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

logger = logging.getLogger("brand_store_import")

PLACE_URL = "https://restapi.amap.com/v5/place/text"
DISTRICT_URL = "https://restapi.amap.com/v3/config/district"
PAGE_SIZE = 25  # 高德单页上限
MAX_PAGES = 8  # 同一组参数最多 200 条
FIRST_PAGE = 1
AMAP_STATUS_OK = "1"
SUBDISTRICT_CITY = 2  # 国家 → 省 → 市
SUBDISTRICT_NEXT = 1
HTTP_TIMEOUT_SEC = 10
REQUEST_INTERVAL_SEC = 0.4
NAME_LIMIT = 256
DESCRIPTION_LIMIT = 512
COORD_DECIMALS = 5
INSERT_BATCH = 200
NO_LIMIT = 0
EXIT_CONFIG = 2
DEFAULT_MYSQL_PORT = 3306
CHINA_LNG_MIN = 73.0
CHINA_LNG_MAX = 136.0
CHINA_LAT_MIN = 3.0
CHINA_LAT_MAX = 54.0
USER_AGENT = "guan-brand-store-import/1.0"
PROGRESS_PATH = os.path.join(SCRIPT_DIR, "data", "brand_store_progress.json")
AMAP_OK = "10000"
EXCLUDE_NAME_PARTS = ("宅急送", "外卖", "配送")
MUNICIPALITIES = frozenset(("北京市", "上海市", "天津市", "重庆市"))
BRAND_ALIASES = {"呷浦呷浦": "呷哺呷哺"}

Brand = namedtuple("Brand", "keyword token image")
City = namedtuple("City", "name adcode province")
Area = namedtuple("Area", "name adcode")
Store = namedtuple(
    "Store", "name description province city area longitude latitude image"
)

# 图片对象名走七牛域名。空字符串表示还没有核对到可用的官方图。
BRANDS = (
    Brand("肯德基", "肯德基", "address/brand/kfc.png"),
    Brand("麦当劳", "麦当劳", "address/brand/mcdonalds.jpg"),
    Brand("杨国福麻辣烫", "杨国福", ""),
    Brand("张亮麻辣烫", "张亮麻辣烫", "address/brand/zhangliang.jpg"),
    Brand("华莱士", "华莱士", "address/brand/wallace.png"),
    Brand("半天妖烤鱼", "半天妖", ""),
    Brand("巫山烤鱼", "巫山烤鱼", ""),
    Brand("呷哺呷哺", "呷哺", "address/brand/xiabu.png"),
    Brand("巴奴火锅", "巴奴", "address/brand/banu.jpg"),
    Brand("小肥羊", "小肥羊", "address/brand/littlesheep.png"),
    Brand("东来顺", "东来顺", "address/brand/donglaishun.png"),
)

INSERT_ADDRESS_SQL = """
INSERT INTO address (name, description, region_id, longitude, latitude, img_obj_name, status)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""
INSERT_REGION_SQL = """
INSERT INTO region (province, city, area, status) VALUES (%s, %s, %s, %s)
"""


class AmapResponseError(Exception):
    def __init__(self, infocode, info):
        self.infocode = infocode
        self.info = info
        super().__init__("高德接口失败 infocode=%s info=%s" % (infocode, info))


def clip(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit]


def plain_text(value):
    if value is None or isinstance(value, (list, dict)):
        return ""
    return str(value).strip()


def store_identity(name, longitude, latitude):
    return (name, round(float(longitude), COORD_DECIMALS), round(float(latitude), COORD_DECIMALS))


def parse_location(text):
    parts = [part.strip() for part in plain_text(text).split(",")]
    if len(parts) != 2:
        return None
    try:
        longitude = float(parts[0])
        latitude = float(parts[1])
    except ValueError:
        return None
    if not (CHINA_LNG_MIN <= longitude <= CHINA_LNG_MAX and CHINA_LAT_MIN <= latitude <= CHINA_LAT_MAX):
        return None
    return longitude, latitude


def store_from_poi(poi, brand, city_name):
    name = clip(plain_text(poi.get("name")), NAME_LIMIT)
    if brand.token not in name:
        return None
    if any(part in name for part in EXCLUDE_NAME_PARTS):
        return None
    point = parse_location(poi.get("location"))
    if not point:
        return None
    longitude, latitude = point
    province = plain_text(poi.get("pname"))
    city = plain_text(poi.get("cityname")) or city_name
    area = plain_text(poi.get("adname"))
    address = plain_text(poi.get("address"))
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


def require_ok(payload):
    if not isinstance(payload, dict):
        raise AmapResponseError("", "响应不是 JSON 对象")
    status = str(payload.get("status", ""))
    infocode = str(payload.get("infocode", ""))
    if status == AMAP_STATUS_OK and infocode in (AMAP_OK, ""):
        return
    raise AmapResponseError(infocode, plain_text(payload.get("info")) or status)


def pois_of(payload):
    require_ok(payload)
    pois = payload.get("pois") or []
    if not isinstance(pois, list):
        return []
    return pois


def cities_from_country(country):
    cities = []
    for province in country.get("districts") or []:
        if province.get("level") != "province":
            continue
        name = plain_text(province.get("name"))
        adcode = plain_text(province.get("adcode"))
        children = [
            child for child in (province.get("districts") or [])
            if child.get("level") == "city" and plain_text(child.get("adcode"))
        ]
        if name in MUNICIPALITIES or not children:
            if name and adcode:
                cities.append(City(name, adcode, name))
            continue
        for child in children:
            cities.append(City(plain_text(child.get("name")), plain_text(child.get("adcode")), name))
    return cities


def split_children(payload):
    """区县可以直接查。直辖市下面先挂着「北京城区」这种市级节点，需要再下一层。"""
    require_ok(payload)
    roots = payload.get("districts") or []
    children = (roots[0].get("districts") if roots else None) or []
    districts = []
    city_codes = []
    for child in children:
        adcode = plain_text(child.get("adcode"))
        if not adcode:
            continue
        if child.get("level") == "district":
            districts.append(Area(plain_text(child.get("name")), adcode))
        elif child.get("level") == "city":
            city_codes.append(adcode)
    return districts, city_codes


def gather_pages(fetch_page, brand, city_name, limit):
    found = []
    for page in range(FIRST_PAGE, MAX_PAGES + 1):
        pois = fetch_page(page)
        for poi in pois:
            store = store_from_poi(poi, brand, city_name)
            if store:
                found.append(store)
        found = dedup_stores(found)
        if limit and len(found) >= limit:
            return found[:limit], False
        if len(pois) < PAGE_SIZE:
            return found, False
    return found, True


def collect_brand_city(search, districts_of, brand, city, limit):
    stores, truncated = search(brand, city.adcode, city.name, limit)
    if not truncated:
        return stores, False
    areas = districts_of(city.adcode)
    if not areas:
        logger.info("城市结果到顶但没有区县可拆 brand=%s city=%s", brand.keyword, city.name)
        return stores, True
    logger.info(
        "城市结果到顶，改按区县查 brand=%s city=%s districts=%s",
        brand.keyword, city.name, len(areas),
    )
    merged = []
    capped = False
    for area in areas:
        part, part_capped = search(brand, area.adcode, city.name, NO_LIMIT)
        if part_capped:
            capped = True
            logger.info("区县结果仍到顶 brand=%s area=%s", brand.keyword, area.name)
        merged.extend(part)
    return dedup_stores(merged), capped


def select_brands(names):
    if not names:
        return list(BRANDS)
    wanted = {BRAND_ALIASES.get(name, name) for name in names}
    return [brand for brand in BRANDS if brand.keyword in wanted or brand.token in wanted]


def city_selected(city, names):
    if not names:
        return True
    for name in names:
        if city.name == name or city.name == name + "市" or name == city.name + "市":
            return True
    return False


def progress_key(brand, city):
    return "%s|%s" % (brand.keyword, city.adcode)


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


def amap_key():
    load_env_file()
    return os.environ.get("AMAP_WEB_KEY", "").strip()


def http_get_json(url, params):
    request = urllib.request.Request(
        url + "?" + urllib.parse.urlencode(params),
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SEC, context=ssl.create_default_context()) as response:
        return json.loads(response.read().decode("utf-8"))


class AmapClient(object):
    def __init__(self, key, get_json, pause):
        self.key = key
        self.get_json = get_json
        self.pause = pause

    def _get(self, url, params):
        query = dict(params)
        query["key"] = self.key
        query["output"] = "json"
        self.pause()
        return self.get_json(url, query)

    def cities(self):
        payload = self._get(DISTRICT_URL, {
            "keywords": "中国",
            "subdistrict": SUBDISTRICT_CITY,
            "extensions": "base",
        })
        require_ok(payload)
        roots = payload.get("districts") or []
        if not roots:
            return []
        return cities_from_country(roots[0])

    def districts(self, adcode):
        payload = self._get(DISTRICT_URL, {
            "keywords": adcode,
            "subdistrict": SUBDISTRICT_NEXT,
            "extensions": "base",
        })
        districts, city_codes = split_children(payload)
        if districts:
            return districts
        found = []
        for code in city_codes:
            sub = self._get(DISTRICT_URL, {
                "keywords": code,
                "subdistrict": SUBDISTRICT_NEXT,
                "extensions": "base",
            })
            more, _ignored = split_children(sub)
            found.extend(more)
        return found

    def search(self, brand, region, city_name, limit):
        def fetch_page(page):
            payload = self._get(PLACE_URL, {
                "keywords": brand.keyword,
                "region": region,
                "city_limit": "true",
                "page_size": PAGE_SIZE,
                "page_num": page,
            })
            return pois_of(payload)

        return gather_pages(fetch_page, brand, city_name, limit)


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
    parser = argparse.ArgumentParser(description="按城市导入连锁餐饮门店")
    parser.add_argument("--brand", action="append", default=[], help="品牌名，可重复。默认全部")
    parser.add_argument("--city", action="append", default=[], help="城市名，可重复。默认全国地级市")
    parser.add_argument("--dry-run", action="store_true", help="只查询并打印数量，不写数据库")
    parser.add_argument("--limit", type=int, default=NO_LIMIT, help="每个城市最多保留多少条，0 表示不限制")
    return parser.parse_args(argv)


def run_import(client, writer, brands, cities, done, limit, record_done):
    inserted_total = 0
    for brand in brands:
        for city in cities:
            mark = progress_key(brand, city)
            if mark in done:
                logger.info("已完成，跳过 brand=%s city=%s", brand.keyword, city.name)
                continue
            stores, capped = collect_brand_city(
                client.search, client.districts, brand, city, limit,
            )
            if writer is None:
                inserted = len(stores)
            else:
                inserted = writer.insert_stores(stores)
            inserted_total += inserted
            logger.info(
                "brand=%s city=%s fetched=%s inserted=%s capped=%s",
                brand.keyword, city.name, len(stores), inserted, capped,
            )
            if record_done:
                done.add(mark)
                save_done(PROGRESS_PATH, done)
    return inserted_total


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = parse_args(sys.argv[1:] if argv is None else argv)
    key = amap_key()
    if not key:
        logger.error("缺少 AMAP_WEB_KEY。请在 guan/.env 填写高德 Web 服务 Key")
        return EXIT_CONFIG
    brands = select_brands(args.brand)
    if args.brand and not brands:
        logger.error("没有匹配的品牌：%s", "、".join(args.brand))
        return EXIT_CONFIG
    client = AmapClient(key, http_get_json, lambda: time.sleep(REQUEST_INTERVAL_SEC))
    cities = [city for city in client.cities() if city_selected(city, args.city)]
    if args.city and not cities:
        logger.error("城市不在高德行政区划里：%s", "、".join(args.city))
        return EXIT_CONFIG
    logger.info("准备导入 brands=%s cities=%s", len(brands), len(cities))
    done = load_done(PROGRESS_PATH)
    record_done = not args.dry_run and not args.limit
    if args.dry_run:
        run_import(client, None, brands, cities, done, args.limit, record_done)
        return 0
    with AddressWriter.connect() as writer:
        run_import(client, writer, brands, cities, done, args.limit, record_done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
