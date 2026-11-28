#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""算出各大城市要补的周末上午场次。不访问数据库。

每次只针对「下一周六」：若本周六上午还有未开始场次则用本周六，否则用再下一个周六。
"""
import datetime

from util.const.progress import MINUTES_PER_HOUR


SLOT_START_HOUR = 9
SLOT_END_HOUR = 12
SLOT_STEP_MINUTES = 30
SATURDAY = 5
DAYS_PER_WEEK = 7


def slot_clocks():
    """9:00 到 12:00，含两端，每半小时一个开始时间。"""
    minute = SLOT_START_HOUR * MINUTES_PER_HOUR
    last_minute = SLOT_END_HOUR * MINUTES_PER_HOUR
    clocks = []
    while minute <= last_minute:
        clocks.append((minute // MINUTES_PER_HOUR, minute % MINUTES_PER_HOUR))
        minute += SLOT_STEP_MINUTES
    return tuple(clocks)


SLOT_CLOCKS = slot_clocks()


def next_saturday_date(day):
    """day 当天或之后最近的周六（含当天若已是周六）。"""
    return day + datetime.timedelta(days=(SATURDAY - day.weekday()) % DAYS_PER_WEEK)


def weekend_slot_times(now):
    """下一周六上午尚未开始的场次。"""
    saturday = next_saturday_date(now.date())
    slots = _future_clocks_on_day(saturday, now)
    if slots:
        return slots
    saturday = saturday + datetime.timedelta(days=DAYS_PER_WEEK)
    return _future_clocks_on_day(saturday, now)


def activities_to_add(address_ids, slots, existing_keys):
    """已有的 (地点, 开始时间) 不再插入。"""
    existing = set(existing_keys)
    missing = []
    for address_id in address_ids:
        for slot in slots:
            key = (address_id, slot)
            if key in existing:
                continue
            missing.append(key)
    return missing


def _future_clocks_on_day(day, now):
    slots = []
    for hour, minute in SLOT_CLOCKS:
        slot = datetime.datetime(day.year, day.month, day.day, hour, minute)
        if slot > now:
            slots.append(slot)
    return slots
