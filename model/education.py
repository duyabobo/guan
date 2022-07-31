#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from model import BaseModel


class EducationModel(BaseModel):
    """教育信息"""
    __tablename__ = 'education'
    id = Column(Integer, primary_key=True)  # id
    school = Column(String, default="")  # 学校
    level = Column(String, default="未知")  # 学历枚举：EDUCATION_CHOICE_LIST
    major = Column(String, default="")  # 专业
