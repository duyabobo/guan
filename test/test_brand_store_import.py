#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from script.brand_store_import import (
    EXIT_CONFIG,
    MAX_PAGES,
    NAME_LIMIT,
    PAGE_SIZE,
    SUBDISTRICT_NEXT,
    Area,
    AmapClient,
    AmapResponseError,
    AddressWriter,
    City,
    address_values,
    cities_from_country,
    city_selected,
    collect_brand_city,
    dedup_stores,
    gather_pages,
    main,
    pois_of,
    require_ok,
    select_brands,
    split_children,
    store_from_poi,
    store_identity,
    BRANDS,
)


def _brand(keyword="肯德基"):
    return next(brand for brand in BRANDS if brand.keyword == keyword)


def _poi(name="肯德基(五道口店)", location="116.34001,39.99001", address="成府路"):
    return {
        "name": name,
        "location": location,
        "address": address,
        "pname": "北京市",
        "cityname": "北京市",
        "adname": "海淀区",
    }


def _store(name="肯德基(五道口店)", location="116.34001,39.99001"):
    return store_from_poi(_poi(name, location), _brand(), "北京市")


def test_store_keeps_brand_shop_inside_china():
    store = _store()
    assert store.name == "肯德基(五道口店)"
    assert store.description == "成府路"
    assert store.province == "北京市"
    assert store.area == "海淀区"
    assert store.image == "address/brand/kfc.png"
    assert store_identity(store.name, store.longitude, store.latitude) == (
        "肯德基(五道口店)", 116.34001, 39.99001,
    )


def test_store_rejects_other_brand_delivery_and_bad_point():
    brand = _brand()
    assert store_from_poi(_poi("麦当劳(五道口店)"), brand, "北京市") is None
    assert store_from_poi(_poi("肯德基宅急送(五道口)"), brand, "北京市") is None
    assert store_from_poi(_poi(location="不是坐标"), brand, "北京市") is None
    assert store_from_poi(_poi(location="2,2"), brand, "北京市") is None
    assert store_from_poi(_poi(location="116.34"), brand, "北京市") is None


def test_empty_address_falls_back_to_admin_names():
    poi = _poi(address=[])
    store = store_from_poi(poi, _brand(), "北京市")
    assert store.description == "北京市 北京市 海淀区"


def test_long_name_is_clipped_before_it_is_stored():
    store = store_from_poi(_poi(name="肯德基" + "店" * NAME_LIMIT), _brand(), "北京市")
    assert len(store.name) == NAME_LIMIT
    assert store.name.startswith("肯德基")


def test_missing_region_id_is_zero():
    values = address_values(_store(), 0)
    assert values[2] == 0
    assert values[5] == "address/brand/kfc.png"


def test_duplicate_shop_is_kept_once():
    first = _store()
    second = _store(location="116.340014,39.990014")
    other = _store(name="肯德基(中关村店)", location="116.32,39.98")
    assert dedup_stores([first, second, other], [store_identity(first.name, first.longitude, first.latitude)]) == [other]


def test_cities_cover_municipality_prefecture_and_bare_province():
    country = {
        "districts": [
            {
                "name": "北京市", "adcode": "110000", "level": "province",
                "districts": [{"name": "北京城区", "adcode": "110100", "level": "city"}],
            },
            {
                "name": "山东省", "adcode": "370000", "level": "province",
                "districts": [{"name": "济南市", "adcode": "370100", "level": "city"}],
            },
            {"name": "香港特别行政区", "adcode": "810000", "level": "province", "districts": []},
        ]
    }
    cities = cities_from_country(country)
    assert [(city.name, city.adcode) for city in cities] == [
        ("北京市", "110000"),
        ("济南市", "370100"),
        ("香港特别行政区", "810000"),
    ]


def test_district_payload_separates_districts_from_city_nodes():
    districts, city_codes = split_children({
        "status": "1",
        "infocode": "10000",
        "districts": [{
            "districts": [
                {"name": "海淀区", "adcode": "110108", "level": "district"},
                {"name": "北京城区", "adcode": "110100", "level": "city"},
            ],
        }],
    })
    assert districts == [Area("海淀区", "110108")]
    assert city_codes == ["110100"]


def test_short_page_stops_and_full_run_is_capped():
    brand = _brand()

    def short(page):
        assert page == 1
        return [_poi()]

    stores, truncated = gather_pages(short, brand, "北京市", 0)
    assert len(stores) == 1
    assert truncated is False

    def full(page):
        return [
            _poi(name="肯德基(店%s-%s)" % (page, index), location="116.%02d,39.%03d" % (page, index))
            for index in range(PAGE_SIZE)
        ]

    stores, truncated = gather_pages(full, brand, "北京市", 0)
    assert truncated is True
    assert len(stores) == PAGE_SIZE * MAX_PAGES


def test_limit_stops_on_the_first_full_page():
    calls = []

    def fetch(page):
        calls.append(page)
        return [_poi(name="肯德基(店%s)" % index, location="116.30,39.%03d" % index) for index in range(PAGE_SIZE)]

    stores, truncated = gather_pages(fetch, _brand(), "北京市", 3)
    assert calls == [1]
    assert truncated is False
    assert len(stores) == 3


def test_client_sends_city_limit_and_turns_the_page():
    calls = []

    def get_json(url, params):
        calls.append(params)
        if int(params["page_num"]) == 1:
            pois = [_poi()] * PAGE_SIZE
        else:
            pois = [_poi(name="肯德基(第二页)", location="116.35,39.99")]
        return {"status": "1", "infocode": "10000", "pois": pois}

    stores, truncated = AmapClient("test-key", get_json, lambda: None).search(_brand(), "110000", "北京市", 0)
    assert truncated is False
    assert [item["page_num"] for item in calls] == [1, 2]
    assert calls[0]["city_limit"] == "true"
    assert calls[0]["key"] == "test-key"
    assert calls[0]["region"] == "110000"
    assert {store.name for store in stores} == {"肯德基(五道口店)", "肯德基(第二页)"}


def test_districts_stop_at_districts_and_follow_a_city_node():
    def direct(url, params):
        assert params["subdistrict"] == SUBDISTRICT_NEXT
        return {"status": "1", "infocode": "10000", "districts": [{"districts": [
            {"name": "海淀区", "adcode": "110108", "level": "district"},
        ]}]}

    areas = AmapClient("k", direct, lambda: None).districts("110000")
    assert areas == [Area("海淀区", "110108")]

    calls = []

    def nested(url, params):
        calls.append(params["keywords"])
        if params["keywords"] == "110000":
            children = [{"name": "北京城区", "adcode": "110100", "level": "city"}]
        else:
            children = [{"name": "海淀区", "adcode": "110108", "level": "district"}]
        return {"status": "1", "infocode": "10000", "districts": [{"districts": children}]}

    areas = AmapClient("k", nested, lambda: None).districts("110000")
    assert calls == ["110000", "110100"]
    assert areas == [Area("海淀区", "110108")]


def test_missing_key_stops_before_request(monkeypatch):
    monkeypatch.setattr("script.brand_store_import.amap_key", lambda: "")
    assert main([]) == EXIT_CONFIG


def test_incomplete_region_is_not_inserted():
    poi = _poi()
    poi["pname"] = ""
    poi["cityname"] = ""
    poi["adname"] = ""
    store = store_from_poi(poi, _brand(), "")
    writer = AddressWriter(_Conn())
    assert writer.insert_stores([store]) == 1
    assert writer.conn.cursor_obj.rows[0][2] == 0
    assert not any("INSERT INTO region" in sql for sql in writer.conn.cursor_obj.calls)


def test_failed_amap_payload_raises():
    with pytest.raises(AmapResponseError) as raised:
        pois_of({"status": "0", "infocode": "10003", "info": "USERKEY_PLAT_NOMATCH", "pois": []})
    assert raised.value.infocode == "10003"
    with pytest.raises(AmapResponseError):
        require_ok(["不是对象"])


def test_capped_city_is_split_and_uncapped_city_is_not():
    brand = _brand()
    city = City("北京市", "110000", "北京市")
    haidian = _store(name="肯德基(海淀店)", location="116.30,39.98")
    chaoyang = _store(name="肯德基(朝阳店)", location="116.48,39.92")
    calls = []

    def search(brand, region, city_name, limit):
        calls.append((region, limit))
        if region == "110000":
            return [_store()], True
        if region == "110108":
            return [haidian], False
        return [chaoyang], True

    stores, capped = collect_brand_city(
        search,
        lambda adcode: [Area("海淀区", "110108"), Area("朝阳区", "110105")],
        brand,
        city,
        0,
    )
    assert calls == [("110000", 0), ("110108", 0), ("110105", 0)]
    assert capped is True
    assert stores == [haidian, chaoyang]

    def city_only(brand, region, city_name, limit):
        return [_store()], False

    stores, capped = collect_brand_city(city_only, lambda adcode: [], brand, city, 0)
    assert capped is False
    assert len(stores) == 1


def test_capped_city_without_districts_keeps_what_it_has():
    kept = _store()

    def search(brand, region, city_name, limit):
        return [kept], True

    stores, capped = collect_brand_city(search, lambda adcode: [], _brand(), City("东莞市", "441900", "广东省"), 0)
    assert stores == [kept]
    assert capped is True


def test_brand_alias_and_city_name_without_suffix():
    brands = select_brands(["呷浦呷浦", "没有这个品牌"])
    assert [brand.keyword for brand in brands] == ["呷哺呷哺"]
    assert select_brands(["不存在"]) == []
    assert city_selected(City("北京市", "110000", "北京市"), ["北京"])
    assert not city_selected(City("济南市", "370100", "山东省"), ["北京"])


class _Cursor(object):
    def __init__(self):
        self.calls = []
        self.last = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.last = sql
        self.calls.append(sql)

    def executemany(self, sql, rows):
        self.calls.append(sql)
        self.rows = list(rows)

    def fetchall(self):
        if "IN (" in self.last:
            return [(9, "北京市", "北京市", "海淀区")]
        return []


class _Conn(object):
    def __init__(self):
        self.cursor_obj = _Cursor()
        self.committed = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def close(self):
        return None


def test_new_region_id_is_written_onto_the_address():
    writer = AddressWriter(_Conn())
    inserted = writer.insert_stores([_store()])
    assert inserted == 1
    assert writer.conn.committed is True
    address_rows = writer.conn.cursor_obj.rows
    assert address_rows[0][2] == 9
    assert writer.insert_stores([_store()]) == 0
