#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 刷新每个用户的匹配的可用的活动id列表
# 活动状态变更后，实时查询会筛选，不需要二次更新。
# 不间断刷新每个用户的匹配的活动id列表，按照区域划分，多进程并发，保持每个用户刷新频次在1分钟内。
