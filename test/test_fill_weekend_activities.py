#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from script.fill_weekend_activities import (
    KFC_IMAGE,
    fill_weekend_activities,
    store_display_name,
)
from service.weekend_activity_supply import weekend_slot_times
from util.const.match import MODEL_ACTIVITY_STATE_EMPTY, MODEL_STATUS_NO, MODEL_STATUS_YES


SATURDAY_MORNING = datetime.datetime(2026, 11, 14, 8, 0)


class _Row:
    def __init__(self, **columns):
        self.__dict__.update(columns)


class _Result:
    def __init__(self, rows, rowcount=0):
        self._rows = rows
        self.rowcount = rowcount

    def fetchall(self):
        return self._rows


class MemorySession:
    """只承接这场供给脚本用到的几条 SQL，方便不连数据库把写入路径跑通。"""

    def __init__(self):
        self.addresses = []
        self.activities = []
        self._next_id = 1

    def add_store(self, name="肯德基", description="", city="", area="", img=KFC_IMAGE):
        row = {
            "id": self._next_id,
            "name": name,
            "description": description,
            "city": city,
            "area": area,
            "status": MODEL_STATUS_YES,
            "img_obj_name": img,
        }
        self._next_id += 1
        self.addresses.append(row)
        return row["id"]

    def execute(self, statement, params=None):
        sql = " ".join(str(statement).split())
        if sql.startswith("SELECT a.id, a.name"):
            return _Result([
                _Row(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    city=row["city"],
                    area=row["area"],
                )
                for row in self.addresses
                if row["status"] == params["status"]
                and row["img_obj_name"] == params["img"]
                and self._is_kfc_name(row["name"])
            ])
        if sql.startswith("UPDATE address SET name"):
            items = params if isinstance(params, list) else [params]
            for item in items:
                for row in self.addresses:
                    if row["id"] == item["id"] and row["status"] == item["status"]:
                        row["name"] = item["name"]
            return _Result([])
        if sql.startswith("UPDATE activity act") and "meetup_name" in (params or {}):
            return self._retire(
                params,
                lambda address: address["name"].endswith("活动点"),
            )
        if sql.startswith("UPDATE activity act") and "kfc_zh" in (params or {}):
            return self._retire(
                params,
                lambda address: (
                    address["img_obj_name"] == params["img"]
                    and not self._is_kfc_name(address["name"])
                ),
            )
        if "FROM activity" in sql:
            address_ids = set(params["address_ids"])
            return _Result([
                _Row(address_id=row["address_id"], start_time=row["start_time"])
                for row in self.activities
                if row["address_id"] in address_ids
                and row["status"] == params["status"]
                and params["start_time"] <= row["start_time"] <= params["end_time"]
            ])
        if sql.startswith("INSERT INTO activity"):
            self.activities.extend(params)
            return _Result([])
        raise AssertionError(sql)

    def _retire(self, params, should_retire):
        retired = 0
        for row in self.activities:
            address = self._address_by_id(row["address_id"])
            if address is None:
                continue
            if (
                row["status"] == params["status_yes"]
                and row["state"] == params["empty_state"]
                and should_retire(address)
            ):
                row["status"] = params["status_no"]
                retired += 1
        return _Result([], rowcount=retired)

    def _address_by_id(self, address_id):
        for row in self.addresses:
            if row["id"] == address_id:
                return row
        return None

    @staticmethod
    def _is_kfc_name(name):
        return "肯德基" in name or "kfc" in name.lower()


def test_store_display_name_uses_street_or_city():
    assert store_display_name("肯德基(沙湾大道店)") == "肯德基(沙湾大道店)"
    assert store_display_name("肯德基", description="文三路") == "肯德基文三路店"
    assert store_display_name("肯德基", description="浙江省 杭州市", city="杭州市") == "肯德基杭州店"
    assert store_display_name("肯德基上海市上海市店", city="上海市") == "肯德基上海店"
    assert store_display_name("肯德基未标注未标注店", description="未标注未标注") == "肯德基门店"
    assert store_display_name("KFC", area="雁塔区") == "肯德基雁塔区店"
    assert store_display_name("肯德基") == "肯德基门店"


def test_fill_writes_kfc_slots_then_skips_existing():
    session = MemorySession()
    session.add_store(name="肯德基南京路店")
    session.add_store(name="肯德基", description="和平路")
    slots = weekend_slot_times(SATURDAY_MORNING)
    created = fill_weekend_activities(session, SATURDAY_MORNING)
    assert created == 2 * len(slots)
    names = {row["name"] for row in session.addresses}
    assert "肯德基南京路店" in names
    assert "肯德基和平路店" in names
    assert {row["state"] for row in session.activities} == {MODEL_ACTIVITY_STATE_EMPTY}
    assert fill_weekend_activities(session, SATURDAY_MORNING) == 0


def test_fill_only_backfills_the_missing_slot():
    session = MemorySession()
    session.add_store(name="肯德基测试店")
    fill_weekend_activities(session, SATURDAY_MORNING)
    session.activities.pop()
    assert fill_weekend_activities(session, SATURDAY_MORNING) == 1
    assert fill_weekend_activities(session, SATURDAY_MORNING) == 0


def test_fill_returns_zero_when_no_kfc_store():
    session = MemorySession()
    session.add_store(name="汉堡王")
    assert fill_weekend_activities(session, SATURDAY_MORNING) == 0
    assert session.activities == []


def test_fill_retires_meetup_and_non_kfc_slots():
    session = MemorySession()
    kfc_id = session.add_store(name="肯德基滨江道店")
    meetup_id = session.add_store(name="天津活动点", img="address/meetup.png")
    burger_id = session.add_store(name="汉堡王")
    slots = weekend_slot_times(SATURDAY_MORNING)
    for address_id in (meetup_id, burger_id):
        session.activities.append({
            "address_id": address_id,
            "start_time": slots[0],
            "state": MODEL_ACTIVITY_STATE_EMPTY,
            "status": MODEL_STATUS_YES,
        })
    created = fill_weekend_activities(session, SATURDAY_MORNING)
    assert created == len(slots)
    retired = [
        row for row in session.activities
        if row["address_id"] in (meetup_id, burger_id)
    ]
    assert all(row["status"] == MODEL_STATUS_NO for row in retired)
    kfc_rows = [row for row in session.activities if row["address_id"] == kfc_id]
    assert len(kfc_rows) == len(slots)
    assert all(row["status"] == MODEL_STATUS_YES for row in kfc_rows)
