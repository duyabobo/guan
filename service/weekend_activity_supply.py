#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""算出各大城市在未来一段时间内要补的周末上午场次。不访问数据库。"""
import datetime

from util.const.progress import LIST_WINDOW_DAYS, MINUTES_PER_HOUR


SUPPLY_LOOKAHEAD_DAYS = LIST_WINDOW_DAYS
SLOT_START_HOUR = 9
SLOT_END_HOUR = 12
SLOT_STEP_MINUTES = 30
SATURDAY = 5
SUNDAY = 6
WEEKEND_DAYS = (SATURDAY, SUNDAY)


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


def weekend_slot_times(now, lookahead_days=SUPPLY_LOOKAHEAD_DAYS):
    """还没到点、并且落在展望窗口内的周六日上午场次。"""
    horizon = now + datetime.timedelta(days=lookahead_days)
    slots = []
    day = now.date()
    while day <= horizon.date():
        if day.weekday() in WEEKEND_DAYS:
            slots.extend(_clocks_on_day(day, now, horizon))
        day += datetime.timedelta(days=1)
    return slots


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


def _clocks_on_day(day, now, horizon):
    slots = []
    for hour, minute in SLOT_CLOCKS:
        slot = datetime.datetime(day.year, day.month, day.day, hour, minute)
        if now < slot <= horizon:
            slots.append(slot)
    return slots
