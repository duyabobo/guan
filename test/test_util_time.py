#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime, time, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from util.util_time import datetime2hommization

_FAR_DAYS = 40


def _at(day, hour, minute):
    return datetime.combine(day, time(hour, minute))


def _clock(moment):
    return moment.strftime("%H:%M")


def test_today_and_tomorrow_take_priority():
    now = datetime.now().replace(second=0, microsecond=0)
    tomorrow = now + timedelta(days=1)
    assert datetime2hommization(now) == "%s(今天) %s" % (now.strftime("%Y-%m-%d"), _clock(now))
    assert datetime2hommization(tomorrow) == "%s(明天) %s" % (tomorrow.strftime("%Y-%m-%d"), _clock(tomorrow))


def test_this_weekend_label_yields_to_today_and_tomorrow():
    today = datetime.now().date()
    this_saturday = today + timedelta(days=(5 - today.weekday() + 7) % 7)
    moment = _at(this_saturday, 10, 0)
    text = datetime2hommization(moment)
    if this_saturday == today:
        assert "(今天)" in text
    elif this_saturday == today + timedelta(days=1):
        assert "(明天)" in text
    else:
        assert text == "%s(本周六) %s" % (this_saturday.strftime("%Y-%m-%d"), "10:00")


def test_next_saturday_and_far_date():
    today = datetime.now().date()
    this_saturday = today + timedelta(days=(5 - today.weekday() + 7) % 7)
    next_saturday = this_saturday + timedelta(days=7)
    weekend = _at(next_saturday, 15, 30)
    assert datetime2hommization(weekend) == "%s(下周六) %s" % (next_saturday.strftime("%Y-%m-%d"), "15:30")

    far = datetime.now().replace(second=0, microsecond=0) + timedelta(days=_FAR_DAYS)
    assert datetime2hommization(far) == far.strftime("%Y-%m-%d %H:%M")
