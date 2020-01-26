#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/20'
# guan_id = 1，用户基本信息问答的 json 数据，这里只是为了方便同步到 redis，其实新增或修改的时候不需要改代码的

USER_INFO_DICT = {
    'step': 1,
    'total_step': 4,
    'service_url': '/user_info',
    'question_dict': {
      1: '你的性别 1/4',
      2: '你的学校 2/4',
      3: '你的身高(cm) 3/4',
      4: '你的年龄(岁) 4/4'
    },
    'answer_dict': {
      1: [
        {
          'key': '女',
          'value': 0,
        },
        {
          'key': '男',
          'value': 1,
        }
      ],
      2: [
        {
          'key': '专科',
          'value': 0,
        },
        {
          'key': '三本',
          'value': 1,
        },
        {
          'key': '二本',
          'value': 2,
        },
        {
          'key': '一本',
          'value': 3,
        },
        {
          'key': '双一流',
          'value': 4,
        },
        {
          'key': '国外大学',
          'value': 5,
        }
      ],
      3: [
        {
          'key': 140,
          'value': 140,
        },
        {
          'key': 145,
          'value': 145,
        },
        {
          'key': 150,
          'value': 150,
        },
        {
          'key': 155,
          'value': 155,
        },
        {
          'key': 160,
          'value': 160,
        },
        {
          'key': 165,
          'value': 165,
        },
        {
          'key': 170,
          'value': 170,
        },
        {
          'key': 175,
          'value': 175,
        },
        {
          'key': 180,
          'value': 180,
        },
        {
          'key': 185,
          'value': 185,
        },
        {
          'key': 190,
          'value': 190,
        },
        {
          'key': 195,
          'value': 195,
        },
      ],
      4: [
        {
          'key': 18,
          'value': 18,
        },
        {
          'key': 19,
          'value': 19,
        },
        {
          'key': 20,
          'value': 20,
        },
        {
          'key': 21,
          'value': 21,
        },
        {
          'key': 22,
          'value': 22,
        },
        {
          'key': 23,
          'value': 23,
        },
        {
          'key': 24,
          'value': 24,
        },
        {
          'key': 25,
          'value': 25,
        },
        {
          'key': 26,
          'value': 26,
        },
        {
          'key': 27,
          'value': 27,
        },
        {
          'key': 28,
          'value': 28,
        },
        {
          'key': 29,
          'value': 28,
        },
        {
          'key': 30,
          'value': 30,
        },
        {
          'key': 31,
          'value': 31,
        },
        {
          'key': 32,
          'value': 32,
        },
        {
          'key': 33,
          'value': 33,
        },
        {
          'key': 34,
          'value': 34,
        },
        {
          'key': 35,
          'value': 35,
        },
        {
          'key': 36,
          'value': 36,
        },
        {
          'key': 37,
          'value': 37,
        },
        {
          'key': 38,
          'value': 38,
        },
        {
          'key': 39,
          'value': 39,
        },
      ]
    }
}
