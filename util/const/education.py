#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.const.base import ALL_STR

DEFAULT_EDUCATION_MULTI_CHOICE_LIST = [ALL_STR]

EDUCATION_MULTI_LIST = [
    [  # 0级
        u"北京市",
        [  # 1级
            u"清华大学",
            [  # 2级
                u"本科",
                [  # 3级
                    u"计算机科学与技术",
                    u"经济学"
                ]
            ],
            [
                u"研究生",
                [
                    u"生物",
                    u"考古"
                ]
            ]
        ],
        [
            u"北京大学",
            [
                u"本科",
                [
                    u"物理学",
                    u"生物学"
                ]
            ]
        ]
    ]
]

DEFAULT_EDUCATION_MULTI_INDEX = 0

