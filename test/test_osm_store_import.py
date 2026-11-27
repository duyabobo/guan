#! /usr/bin/env python
# -*- coding: utf-8 -*-
from script.osm_city_bbox import CITY_BBOX_ROWS
from script.osm_store_import import (
    BRANDS,
    CITY_BBOXES,
    DEFAULT_PBF_PATH,
    EXIT_CONFIG,
    FALLBACK_CITY,
    GEOFABRIK_CHINA_PBF_URL,
    MAJOR_CITIES,
    TIER1_NEW_TIER1_NAMES,
    AddressWriter,
    City,
    Store,
    admin_from_tags,
    admin_stem,
    brand_of_tags,
    city_containing,
    dedup_stores,
    place_selected,
    resolve_admin,
    resolve_pbf_path,
    store_from_wgs,
    store_identity,
    stores_from_points,
    wgs84_to_gcj02,
)


def _beijing():
    return City("北京市", "北京市", 39.40, 115.70, 41.10, 117.50)


def _tags(name="肯德基(五道口店)", **extra):
    tags = {
        "name": name,
        "brand:wikidata": "Q177054",
        "addr:district": "海淀区",
        "addr:street": "成府路",
    }
    tags.update(extra)
    return tags


def test_wgs84_to_gcj02_shifts_beijing_point():
    lng, lat = wgs84_to_gcj02(116.397128, 39.916527)
    assert abs(lng - 116.397128) > 0.001
    assert abs(lat - 39.916527) > 0.001
    assert 116.3 < lng < 116.5
    assert 39.8 < lat < 40.0


def test_wgs84_outside_china_stays_unchanged():
    assert wgs84_to_gcj02(0.0, 0.0) == (0.0, 0.0)


def test_store_from_wgs_converts_and_keeps_brand():
    store = store_from_wgs(_tags(), 116.34001, 39.99001, [_beijing()])
    assert store.name == "肯德基(五道口店)"
    assert store.city == "北京市"
    assert store.area == "海淀区"
    assert store.description == "成府路"
    assert store.image == "address/brand/kfc.png"
    assert store.longitude != 116.34001


def test_store_rejects_delivery_and_outside_china():
    assert store_from_wgs(_tags(name="肯德基宅急送(五道口)"), 116.34, 39.99, [_beijing()]) is None
    assert store_from_wgs(_tags(), 2.0, 2.0, [_beijing()]) is None


def test_mcdonald_and_empty_address_fallback():
    tags = _tags(
        "麦当劳(五道口店)",
        **{"brand:wikidata": "Q38076", "addr:street": "", "addr:full": ""},
    )
    store = store_from_wgs(tags, 116.34, 39.99, [_beijing()])
    assert store.image == "address/brand/mcdonalds.jpg"
    assert store.description == "北京市 北京市 海淀区"


def test_brand_of_tags_matches_name_fallback():
    assert brand_of_tags({"name": "麦当劳餐厅"}).keyword == "麦当劳"
    assert brand_of_tags({"brand:en": "KFC"}).keyword == "肯德基"
    assert brand_of_tags({"name": "一点点"}) is None


def test_city_containing_and_admin_stem():
    assert city_containing(116.40, 39.90, MAJOR_CITIES).name == "北京市"
    assert city_containing(121.47, 31.23, MAJOR_CITIES).name == "上海市"
    assert city_containing(100.0, 20.0, MAJOR_CITIES) is None
    assert admin_stem("北京市") == "北京"
    assert admin_stem("西峡县") == "西峡"
    assert admin_stem("海淀区") == "海淀"
    assert admin_stem("凉山彝族自治州") == "凉山彝族"


def test_admin_from_tags_prefers_county():
    province, city, area = admin_from_tags(
        {
            "addr:province": "河南省",
            "addr:city": "南阳市",
            "addr:county": "西峡县",
            "addr:district": "某区",
        }
    )
    assert (province, city, area) == ("河南省", "南阳市", "西峡县")


def test_resolve_admin_uses_tags_outside_bbox():
    tags = {
        "addr:province": "云南省",
        "addr:city": "丽江市",
        "addr:county": "玉龙纳西族自治县",
    }
    province, city, area = resolve_admin(tags, 100.2, 26.9, [_beijing()])
    assert province == "云南省"
    assert city == "丽江市"
    assert area == "玉龙纳西族自治县"


def test_resolve_admin_fallback_when_no_tags_or_bbox():
    province, city, area = resolve_admin({}, 100.0, 20.0, [_beijing()])
    assert province == "未标注"
    assert city == FALLBACK_CITY
    assert area == ""


def test_stores_from_points_covers_nation_and_place_filter():
    points = [
        (_tags(), 116.34, 39.99),
        (
            _tags(
                name="肯德基(西峡店)",
                **{
                    "addr:province": "河南省",
                    "addr:city": "南阳市",
                    "addr:county": "西峡县",
                    "addr:district": "",
                },
            ),
            111.48,
            33.30,
        ),
        (_tags(name="肯德基宅急送"), 116.35, 39.98),
    ]
    stores = stores_from_points(points, [_beijing()])
    assert len(stores) == 2
    assert {store.city for store in stores} == {"北京市", "南阳市"}
    county_only = stores_from_points(points, [_beijing()], place_names=["西峡县"])
    assert len(county_only) == 1
    assert county_only[0].area == "西峡县"
    assert place_selected(county_only[0], ["西峡"]) is True


def test_dedup_stores():
    first = store_from_wgs(_tags(), 116.34, 39.99, [_beijing()])
    second = store_from_wgs(_tags(), 116.34, 39.99, [_beijing()])
    assert len(dedup_stores([first, second])) == 1
    assert store_identity(first.name, first.longitude, first.latitude)[0] == first.name


def test_region_key_allows_empty_area():
    writer = AddressWriter.__new__(AddressWriter)
    writer.regions = {}
    with_area = Store(
        "肯德基(五道口店)", "成府路", "北京市", "北京市", "海淀区", 116.34, 39.99, "address/brand/kfc.png",
    )
    no_area = Store(
        "麦当劳(中关村)", "北京市 北京市", "北京市", "北京市", "", 116.31, 39.98, "address/brand/mcdonalds.jpg",
    )
    no_city = Store("肯德基", "x", "北京市", "", "", 116.3, 39.9, "address/brand/kfc.png")
    assert writer._region_key(with_area) == ("北京市", "北京市", "海淀区")
    assert writer._region_key(no_area) == ("北京市", "北京市", "")
    assert writer._region_key(no_city) is None
    assert writer._missing_regions([with_area, no_area, no_area, no_city]) == [
        ("北京市", "北京市", "海淀区"),
        ("北京市", "北京市", ""),
    ]
    writer.regions[("北京市", "北京市", "")] = 1
    assert writer._missing_regions([no_area]) == []


def test_store_without_district_keeps_empty_area():
    tags = _tags(
        **{
            "addr:district": "",
            "addr:suburb": "",
            "addr:city_district": "",
            "addr:county": "",
            "addr:street": "",
            "addr:full": "",
        }
    )
    store = store_from_wgs(tags, 116.34, 39.99, [_beijing()])
    assert store.area == ""
    assert store.description == "北京市 北京市"


def test_resolve_pbf_path_uses_existing_file(tmp_path):
    pbf = tmp_path / "china-latest.osm.pbf"
    pbf.write_bytes(b"pbf")
    args = type("Args", (), {"pbf": str(pbf), "download": True})()
    assert resolve_pbf_path(args) == str(pbf)


def test_resolve_pbf_path_requires_download_when_missing(tmp_path):
    missing = tmp_path / "missing.osm.pbf"
    args = type("Args", (), {"pbf": str(missing), "download": False})()
    assert resolve_pbf_path(args) == ""


def test_download_defaults_and_city_bbox_coverage():
    assert GEOFABRIK_CHINA_PBF_URL.endswith("china-latest.osm.pbf")
    assert DEFAULT_PBF_PATH.endswith("china-latest.osm.pbf")
    assert EXIT_CONFIG == 2
    assert {brand.keyword for brand in BRANDS} == {"肯德基", "麦当劳"}
    assert len(MAJOR_CITIES) == len(TIER1_NEW_TIER1_NAMES)
    assert len(CITY_BBOXES) >= 100
    assert city_containing(112.50, 33.00, CITY_BBOXES).name == "南阳市"


def test_city_bbox_rows_unique_and_valid():
    names = [row[0] for row in CITY_BBOX_ROWS]
    assert len(names) == len(set(names))
    for name, province, south, west, north, east in CITY_BBOX_ROWS:
        assert name and province
        assert south < north
        assert west < east
