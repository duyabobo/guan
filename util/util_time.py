#!/usr/bin/python
# -*- coding=utf-8 -*-
# 前后端的时间传输都是通过时间戳传递, 后端处理时间都是精确到秒, 时间戳 -1 对应时间 None
from datetime import datetime, timedelta


def datetime2timestamp(d):
    d = str(d)
    if d:
        return int(datetime.strptime(d, '%Y-%m-%d %H:%M:%S').strftime('%s000'))
    else:
        return -1


def timestamp2datetime(t):
    t = int(t)
    if t != -1:
        return datetime.fromtimestamp(t/1000)
    else:
        return None


def date2timestamp(d):
    d = str(d)
    if d:
        return int(datetime.strptime(d, '%Y-%m-%d').strftime('%s000'))
    else:
        return -1


def timestamp2date(t):
    t = int(t)
    if t != -1:
        return datetime.fromtimestamp(t / 1000).date()
    else:
        return None


def datetime2str(d, fmt="%Y-%m-%d %H:%M:%S"):
    return d.strftime(fmt)

def datetime2hommization(d):
    """
    把日期转成人性化友好的字符格式：
    1. 今天就显示`今天 %H:%M:%S`
    2. 明天就显示`明天 %H:%M:%S`
    3. 其他情况：
        3.1 本周六，就展示 `本周六 %H:%M`
        3.2 本周日，就展示 `本周日 %H:%M`
        3.3 下周六，就展示 `下周六 %H:%M`
        3.4 下周日，就展示 `下周日 %H:%M`
        3.3 其他，就直接显示 `%Y-%m-%d %H:%M`
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

# 测试代码
if __name__ == "__main__":
    now = datetime.now()
    test_dates = [
        now,  # 今天
        now + timedelta(days=1),  # 明天
        now + timedelta(days=3),  # 后天
        now + timedelta(days=(5 - now.weekday()) % 7 + 7),  # 下周六
        now + timedelta(days=(6 - now.weekday()) % 7 + 7),  # 下周日
        now + timedelta(days=10),  # 随意未来日期
    ]

    for test_date in test_dates:
        print("{}: {}".format(test_date, datetime2hommization(test_date)))

