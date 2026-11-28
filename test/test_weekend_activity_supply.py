#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from script.major_cities import MAJOR_CITY_VENUES
from service.weekend_activity_supply import (
    DAYS_PER_WEEK,
    SATURDAY as SATURDAY_WEEKDAY,
    SLOT_CLOCKS,
    SLOT_END_HOUR,
    SLOT_START_HOUR,
    activities_to_add,
    next_saturday_date,
    weekend_slot_times,
)
from util.const.match import LATITUDE_MAX, LATITUDE_MIN, LONGITUDE_MAX, LONGITUDE_MIN


SATURDAY = datetime.date(2026, 11, 14)
NEXT_SATURDAY = SATURDAY + datetime.timedelta(days=DAYS_PER_WEEK)


def _at(day, hour, minute=0):
    return datetime.datetime(day.year, day.month, day.day, hour, minute)


def test_clocks_cover_nine_to_noon_every_half_hour():
    assert SLOT_CLOCKS[0] == (SLOT_START_HOUR, 0)
    assert SLOT_CLOCKS[-1] == (SLOT_END_HOUR, 0)
    assert SLOT_CLOCKS == (
        (9, 0), (9, 30), (10, 0), (10, 30), (11, 0), (11, 30), (12, 0),
    )


def test_weekday_targets_coming_saturday():
    wednesday = _at(datetime.date(2026, 11, 11), 8, 0)
    slots = weekend_slot_times(wednesday)
    assert {slot.date() for slot in slots} == {SATURDAY}
    assert slots[0] == _at(SATURDAY, 9, 0)
    assert slots[-1] == _at(SATURDAY, 12, 0)
    assert len(slots) == len(SLOT_CLOCKS)


def test_saturday_morning_only_fills_today_saturday():
    now = _at(SATURDAY, 8, 0)
    slots = weekend_slot_times(now)
    assert slots[0] == _at(SATURDAY, 9, 0)
    assert slots[-1] == _at(SATURDAY, 12, 0)
    assert {slot.date() for slot in slots} == {SATURDAY}
    assert len(slots) == len(SLOT_CLOCKS)
    assert all(slot.weekday() == SATURDAY_WEEKDAY for slot in slots)


def test_slot_equal_to_now_is_left_out_and_past_saturday_rolls_forward():
    at_nine = weekend_slot_times(_at(SATURDAY, 9, 0))
    assert _at(SATURDAY, 9, 0) not in at_nine
    assert _at(SATURDAY, 9, 30) in at_nine
    assert all(slot.date() == SATURDAY for slot in at_nine)

    before_noon = weekend_slot_times(
        _at(SATURDAY, SLOT_END_HOUR) - datetime.timedelta(minutes=1),
    )
    assert _at(SATURDAY, SLOT_END_HOUR) in before_noon

    at_noon = weekend_slot_times(_at(SATURDAY, SLOT_END_HOUR))
    assert _at(SATURDAY, SLOT_END_HOUR) not in at_noon
    assert {slot.date() for slot in at_noon} == {NEXT_SATURDAY}
    assert at_noon[0] == _at(NEXT_SATURDAY, 9, 0)
    assert at_noon[-1] == _at(NEXT_SATURDAY, 12, 0)


def test_friday_night_fills_tomorrow_saturday():
    friday_night = _at(datetime.date(2026, 11, 13), 23, 0)
    slots = weekend_slot_times(friday_night)
    assert _at(SATURDAY, 12, 0) in slots
    assert all(slot.date() == SATURDAY for slot in slots)


def test_next_saturday_date_includes_today_when_saturday():
    assert next_saturday_date(SATURDAY) == SATURDAY
    assert next_saturday_date(datetime.date(2026, 11, 13)) == SATURDAY
    assert next_saturday_date(datetime.date(2026, 11, 15)) == NEXT_SATURDAY


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
