#!/usr/bin/python
# -*- coding=utf-8 -*-
from datetime import datetime, timedelta


def datetime2hommization(d):
    """
    把日期转成列表上的时间文案，精确到分钟。
    今天、明天优先；再标本周或下周的周六日；其余只显示日期和时间。
    """
    now = datetime.now()
    today = now.date()
    tomorrow = today + timedelta(days=1)

    # 将日期转换为日期对象，仅保留年月日
    input_date = d.date()

    # 如果是今天
    _d = d.strftime('%Y-%m-%d')
    _t = d.strftime('%H:%M')
    if input_date == today:
        return "{}(今天) {}".format(_d, _t)
    # 如果是明天
    elif input_date == tomorrow:
        return "{}(明天) {}".format(_d, _t)
    else:
        # 获取输入日期的星期编号（周一为0，周日为6）
        this_saturday = today + timedelta(days=(5 - today.weekday() + 7) % 7)
        this_sunday = today + timedelta(days=(6 - today.weekday() + 7) % 7)
        next_saturday = today + timedelta(days=(5 - today.weekday() + 7) % 7 + 7)
        next_sunday = today + timedelta(days=(6 - today.weekday() + 7) % 7 + 7)

        if input_date == this_saturday:
            return "{}(本周六) {}".format(_d, _t)
        elif input_date == this_sunday:
            return "{}(本周日) {}".format(_d, _t)
        elif input_date == next_saturday:
            return "{}(下周六) {}".format(_d, _t)
        elif input_date == next_sunday:
            return "{}(下周日) {}".format(_d, _t)
        else:
            # 默认情况显示完整日期时间
            return d.strftime('%Y-%m-%d %H:%M')

