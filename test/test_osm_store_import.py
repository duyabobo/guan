#! /usr/bin/env python
# -*- coding: utf-8 -*-
from script.osm_store_import import (
    BRANDS,
    MAJOR_CITIES,
    City,
    brand_of_tags,
    city_selected,
    dedup_stores,
    overpass_query,
    run_import,
    store_from_element,
    store_identity,
    wgs84_to_gcj02,
)


def _beijing():
    return City("北京市", "北京市", 39.40, 115.70, 41.10, 117.50)


def _element(name="肯德基(五道口店)", lon=116.34001, lat=39.99001, tags=None):
    base = {
        "name": name,
        "brand:wikidata": "Q177054",
        "addr:district": "海淀区",
        "addr:street": "成府路",
    }
    if tags:
        base.update(tags)
    return {"type": "node", "lat": lat, "lon": lon, "tags": base}


class _FakeClient(object):
    def __init__(self, stores_by_city):
        self.stores_by_city = stores_by_city
        self.calls = []

    def fetch_city(self, city):
        self.calls.append(city.name)
        return list(self.stores_by_city.get(city.name, []))


def test_wgs84_to_gcj02_shifts_beijing_point():
    lng, lat = wgs84_to_gcj02(116.397128, 39.916527)
    assert abs(lng - 116.397128) > 0.001
    assert abs(lat - 39.916527) > 0.001
    assert 116.3 < lng < 116.5
    assert 39.8 < lat < 40.0


def test_wgs84_outside_china_stays_unchanged():
    lng, lat = wgs84_to_gcj02(0.0, 0.0)
    assert (lng, lat) == (0.0, 0.0)


def test_store_from_element_converts_and_keeps_brand():
    store = store_from_element(_element(), _beijing())
    assert store.name == "肯德基(五道口店)"
    assert store.city == "北京市"
    assert store.area == "海淀区"
    assert store.description == "成府路"
    assert store.image == "address/brand/kfc.png"
    assert store.longitude != 116.34001


def test_store_rejects_delivery_and_outside_china():
    assert store_from_element(_element(name="肯德基宅急送(五道口)"), _beijing()) is None
    assert store_from_element(_element(lon=2.0, lat=2.0), _beijing()) is None


def test_mcdonald_and_empty_address_fallback():
    mcdonald = _element(
        name="麦当劳(五道口店)",
        tags={
            "brand:wikidata": "Q38076",
            "name": "麦当劳(五道口店)",
            "addr:district": "海淀区",
            "addr:street": "",
            "addr:full": "",
        },
    )
    store = store_from_element(mcdonald, _beijing())
    assert store.image == "address/brand/mcdonalds.jpg"
    assert store.description == "北京市 北京市 海淀区"


def test_brand_of_tags_matches_name_fallback():
    assert brand_of_tags({"name": "麦当劳餐厅"}).keyword == "麦当劳"
    assert brand_of_tags({"brand:en": "KFC"}).keyword == "肯德基"
    assert brand_of_tags({"name": "一点点"}) is None


def test_way_uses_center_point():
    element = {
        "type": "way",
        "center": {"lat": 39.99, "lon": 116.34},
        "tags": {"name": "肯德基", "brand:wikidata": "Q177054"},
    }
    store = store_from_element(element, _beijing())
    assert store is not None
    assert store_identity(store.name, store.longitude, store.latitude)[0] == "肯德基"


def test_dedup_and_city_selected():
    first = store_from_element(_element(), _beijing())
    second = store_from_element(_element(), _beijing())
    assert len(dedup_stores([first, second])) == 1
    assert city_selected(_beijing(), []) is True
    assert city_selected(_beijing(), ["北京"]) is True
    assert city_selected(_beijing(), ["北京市"]) is True
    assert city_selected(_beijing(), ["上海"]) is False
    assert city_selected(_beijing(), ["北"]) is False


def test_overpass_query_covers_both_brands():
    query = overpass_query(_beijing())
    assert "Q177054" in query
    assert "Q38076" in query
    assert "肯德基" in query
    assert "麦当劳" in query


def test_run_import_skips_done_and_counts_fetched():
    store = store_from_element(_element(), _beijing())
    client = _FakeClient({"北京市": [store], "上海市": [store]})
    cities = [_beijing(), City("上海市", "上海市", 30.0, 120.0, 31.0, 121.0)]
    done = {"北京市"}
    inserted = run_import(client, None, cities, done, False)
    assert client.calls == ["上海市"]
    assert inserted == 1
    assert done == {"北京市"}


def test_major_cities_and_brands_are_ready():
    assert len(MAJOR_CITIES) >= 15
    assert {brand.keyword for brand in BRANDS} == {"肯德基", "麦当劳"}
