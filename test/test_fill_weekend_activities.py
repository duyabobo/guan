#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import pytest

from script.fill_weekend_activities import fill_weekend_activities
from script.major_cities import MAJOR_CITY_VENUES
from service.weekend_activity_supply import weekend_slot_times
from util.const.match import MODEL_ACTIVITY_STATE_EMPTY


SATURDAY_MORNING = datetime.datetime(2026, 11, 14, 8, 0)


class _Row:
    def __init__(self, **columns):
        self.__dict__.update(columns)


class _Result:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return self._rows


class MemorySession:
    """只承接这场供给脚本用到的几条 SQL，方便不连数据库把写入路径跑通。"""

    def __init__(self):
        self.regions = []
        self.addresses = []
        self.activities = []
        self._next_id = 1

    def execute(self, statement, params=None):
        sql = " ".join(str(statement).split())
        if sql.startswith("SELECT id, province"):
            return _Result([_Row(**row) for row in self.regions])
        if sql.startswith("INSERT INTO region"):
            self.regions.extend(self._with_ids(params))
            return _Result([])
        if "FROM address" in sql:
            names = set(params["names"])
            return _Result([
                _Row(id=row["id"], name=row["name"])
                for row in self.addresses
                if row["name"] in names and row["status"] == params["status"]
            ])
        if sql.startswith("INSERT INTO address"):
            self.addresses.extend(self._with_ids(params))
            return _Result([])
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

    def _with_ids(self, rows):
        stored = []
        for row in rows:
            copied = dict(row)
            copied["id"] = self._next_id
            self._next_id += 1
            stored.append(copied)
        return stored


class _SkipInsert(MemorySession):
    def __init__(self, sql_prefix):
        super().__init__()
        self.sql_prefix = sql_prefix

    def execute(self, statement, params=None):
        sql = " ".join(str(statement).split())
        if sql.startswith(self.sql_prefix):
            return _Result([])
        return super().execute(statement, params)


def test_fill_writes_every_city_then_skips_existing():
    session = MemorySession()
    slots = weekend_slot_times(SATURDAY_MORNING)
    created = fill_weekend_activities(session, SATURDAY_MORNING)
    assert created == len(MAJOR_CITY_VENUES) * len(slots)
    assert len(session.addresses) == len(MAJOR_CITY_VENUES)
    assert {row["state"] for row in session.activities} == {MODEL_ACTIVITY_STATE_EMPTY}
    assert fill_weekend_activities(session, SATURDAY_MORNING) == 0


def test_fill_only_backfills_the_missing_slot():
    session = MemorySession()
    fill_weekend_activities(session, SATURDAY_MORNING)
    session.activities.pop()
    assert fill_weekend_activities(session, SATURDAY_MORNING) == 1
    assert fill_weekend_activities(session, SATURDAY_MORNING) == 0


def test_fill_fails_when_region_insert_does_not_land():
    with pytest.raises(RuntimeError, match="省市区没有写上"):
        fill_weekend_activities(_SkipInsert("INSERT INTO region"), SATURDAY_MORNING)


def test_fill_fails_when_address_insert_does_not_land():
    with pytest.raises(RuntimeError, match="见面点没有写上"):
        fill_weekend_activities(_SkipInsert("INSERT INTO address"), SATURDAY_MORNING)
