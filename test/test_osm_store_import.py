#! /usr/bin/env python
# -*- coding: utf-8 -*-
from script.osm_store_import import (
    BRANDS,
    DEFAULT_PBF_PATH,
    EXIT_CONFIG,
    GEOFABRIK_CHINA_PBF_URL,
    MAJOR_CITIES,
    City,
    brand_of_tags,
    city_containing,
    city_selected,
    dedup_stores,
    resolve_pbf_path,
    store_from_wgs,
    store_identity,
    stores_from_points,
    way_center,
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
    store = store_from_wgs(_tags(), 116.34001, 39.99001, _beijing())
    assert store.name == "肯德基(五道口店)"
    assert store.city == "北京市"
    assert store.area == "海淀区"
    assert store.description == "成府路"
    assert store.image == "address/brand/kfc.png"
    assert store.longitude != 116.34001


def test_store_rejects_delivery_and_outside_china():
    assert store_from_wgs(_tags(name="肯德基宅急送(五道口)"), 116.34, 39.99, _beijing()) is None
    assert store_from_wgs(_tags(), 2.0, 2.0, _beijing()) is None


def test_mcdonald_and_empty_address_fallback():
    tags = _tags(
        "麦当劳(五道口店)",
        **{"brand:wikidata": "Q38076", "addr:street": "", "addr:full": ""},
    )
    store = store_from_wgs(tags, 116.34, 39.99, _beijing())
    assert store.image == "address/brand/mcdonalds.jpg"
    assert store.description == "北京市 北京市 海淀区"


def test_brand_of_tags_matches_name_fallback():
    assert brand_of_tags({"name": "麦当劳餐厅"}).keyword == "麦当劳"
    assert brand_of_tags({"brand:en": "KFC"}).keyword == "肯德基"
    assert brand_of_tags({"name": "一点点"}) is None


def test_city_containing_and_selected():
    assert city_containing(116.40, 39.90, MAJOR_CITIES).name == "北京市"
    assert city_containing(121.47, 31.23, MAJOR_CITIES).name == "上海市"
    assert city_containing(100.0, 20.0, MAJOR_CITIES) is None
    assert city_selected(_beijing(), []) is True
    assert city_selected(_beijing(), ["北京"]) is True
    assert city_selected(_beijing(), ["北"]) is False


def test_stores_from_points_filters_by_city_bbox():
    points = [
        (_tags(), 116.34, 39.99),
        (_tags(name="肯德基(外地)"), 100.0, 20.0),
        (_tags(name="肯德基宅急送"), 116.35, 39.98),
    ]
    stores = stores_from_points(points, [_beijing()])
    assert len(stores) == 1
    assert stores[0].name == "肯德基(五道口店)"


def test_dedup_stores():
    first = store_from_wgs(_tags(), 116.34, 39.99, _beijing())
    second = store_from_wgs(_tags(), 116.34, 39.99, _beijing())
    assert len(dedup_stores([first, second])) == 1
    assert store_identity(first.name, first.longitude, first.latitude)[0] == first.name


def test_way_center_averages_nodes():
    class _Loc(object):
        def __init__(self, valid=True):
            self._valid = valid

        def valid(self):
            return self._valid

    class _Node(object):
        def __init__(self, lon, lat, valid=True):
            self.lon = lon
            self.lat = lat
            self.location = _Loc(valid)

    class _Way(object):
        def __init__(self, nodes):
            self.nodes = nodes

    assert way_center(_Way([])) is None
    assert way_center(_Way([_Node(116.0, 40.0, valid=False)])) is None
    lng, lat = way_center(_Way([_Node(116.0, 40.0), _Node(118.0, 42.0)]))
    assert (lng, lat) == (117.0, 41.0)


def test_resolve_pbf_path_uses_existing_file(tmp_path):
    pbf = tmp_path / "china-latest.osm.pbf"
    pbf.write_bytes(b"pbf")
    args = type("Args", (), {"pbf": str(pbf), "download": True})()
    assert resolve_pbf_path(args) == str(pbf)


def test_resolve_pbf_path_requires_download_when_missing(tmp_path):
    missing = tmp_path / "missing.osm.pbf"
    args = type("Args", (), {"pbf": str(missing), "download": False})()
    assert resolve_pbf_path(args) == ""


def test_download_defaults_point_to_china_pbf():
    assert GEOFABRIK_CHINA_PBF_URL.endswith("china-latest.osm.pbf")
    assert DEFAULT_PBF_PATH.endswith("china-latest.osm.pbf")
    assert EXIT_CONFIG == 2
    assert {brand.keyword for brand in BRANDS} == {"肯德基", "麦当劳"}
    assert len(MAJOR_CITIES) >= 15
