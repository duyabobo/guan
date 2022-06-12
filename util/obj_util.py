#! /usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal


def object_2_dict(input_object, witharr=False):
    """将结构体对象序列化为dict结构"""
    if input_object.__class__.__name__ in ('list', 'tuple', 'set'):
        output_list = [object_2_dict(v, witharr) for v in input_object]
        return output_list

    if input_object.__class__.__name__ in ('dict',):
        output_dict = dict((k, object_2_dict(v, witharr))
                           for k, v in input_object.items())
        return output_dict

    if hasattr(input_object, '__dict__'):
        output_dict = dict((k, object_2_dict(v, witharr))
                           for k, v in input_object.__dict__.items())
        if witharr:
            output_dict['__class__'] = input_object.__class__.__name__
            output_dict['__module__'] = input_object.__module__
        return output_dict

    # 日期类型转换
    if isinstance(input_object, datetime):
        return input_object.strftime('%Y-%m-%d %H:%M:%S')
    # decimal数据类型转换成float型
    if isinstance(input_object, Decimal):
        return float(input_object)

    return input_object
