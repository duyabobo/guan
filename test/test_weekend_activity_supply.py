#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from script.major_cities import MAJOR_CITY_VENUES
from service.weekend_activity_supply import (
    SLOT_CLOCKS,
    SLOT_END_HOUR,
    SLOT_START_HOUR,
    WEEKEND_DAYS,
    activities_to_add,
    weekend_slot_times,
)
from util.const.match import LATITUDE_MAX, LATITUDE_MIN, LONGITUDE_MAX, LONGITUDE_MIN


SATURDAY = datetime.date(2026, 11, 14)
SUNDAY = datetime.date(2026, 11, 15)


def _at(day, hour, minute=0):
    return datetime.datetime(day.year, day.month, day.day, hour, minute)


def test_clocks_cover_nine_to_noon_every_half_hour():
    assert SLOT_CLOCKS[0] == (SLOT_START_HOUR, 0)
    assert SLOT_CLOCKS[-1] == (SLOT_END_HOUR, 0)
    assert SLOT_CLOCKS == (
        (9, 0), (9, 30), (10, 0), (10, 30), (11, 0), (11, 30), (12, 0),
    )


def test_weekday_inside_short_window_has_no_slot():
    wednesday = _at(datetime.date(2026, 11, 11), 8, 0)
    assert weekend_slot_times(wednesday, lookahead_days=2) == []


def test_saturday_morning_includes_today_and_sunday():
    now = _at(SATURDAY, 8, 0)
    slots = weekend_slot_times(now, lookahead_days=2)
    assert slots[0] == _at(SATURDAY, 9, 0)
    assert slots[-1] == _at(SUNDAY, 12, 0)
    assert {slot.date() for slot in slots} == {SATURDAY, SUNDAY}
    assert len(slots) == len(SLOT_CLOCKS) * len(WEEKEND_DAYS)
    assert all(slot.weekday() in WEEKEND_DAYS for slot in slots)


def test_slot_equal_to_now_is_left_out_and_noon_is_kept():
    at_nine = weekend_slot_times(_at(SATURDAY, 9, 0), lookahead_days=1)
    assert _at(SATURDAY, 9, 0) not in at_nine
    assert _at(SATURDAY, 9, 30) in at_nine

    before_noon = weekend_slot_times(
        _at(SATURDAY, SLOT_END_HOUR) - datetime.timedelta(minutes=1), lookahead_days=1,
    )
    assert _at(SATURDAY, SLOT_END_HOUR) in before_noon

    at_noon = weekend_slot_times(_at(SATURDAY, SLOT_END_HOUR), lookahead_days=1)
    assert _at(SATURDAY, SLOT_END_HOUR) not in at_noon
    assert _at(SUNDAY, SLOT_START_HOUR) in at_noon
    assert _at(SUNDAY, SLOT_END_HOUR) in at_noon
    assert all(slot.date() != SATURDAY for slot in at_noon)


def test_slot_past_the_horizon_is_left_out():
    friday_night = _at(datetime.date(2026, 11, 13), 23, 0)
    slots = weekend_slot_times(friday_night, lookahead_days=1)
    assert _at(SATURDAY, 12, 0) in slots
    assert all(slot.date() == SATURDAY for slot in slots)


def test_activities_skip_existing_and_fill_gaps():
    slots = (_at(SATURDAY, 9, 0), _at(SATURDAY, 9, 30))
    existing = {(1, slots[0])}
    assert activities_to_add([1, 2], slots, existing) == [
        (1, slots[1]),
        (2, slots[0]),
        (2, slots[1]),
    ]


def test_activities_to_add_is_empty_without_addresses_or_slots():
    slot = _at(SATURDAY, 9, 0)
    assert activities_to_add([], [slot], set()) == []
    assert activities_to_add([1], [], {(1, slot)}) == []


def test_major_cities_are_unique_and_on_the_map():
    names = [venue.name for venue in MAJOR_CITY_VENUES]
    cities = [venue.city for venue in MAJOR_CITY_VENUES]
    assert len(names) == len(set(names))
    assert len(cities) == len(set(cities))
    assert "北京市" in cities and "乌鲁木齐市" in cities
    for venue in MAJOR_CITY_VENUES:
        assert venue.province and venue.area
        assert LONGITUDE_MIN <= venue.longitude <= LONGITUDE_MAX
        assert LATITUDE_MIN <= venue.latitude <= LATITUDE_MAX
