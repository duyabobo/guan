#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from model.education import EducationModel
from model.region import RegionModel
from model.verify import VerifyModel
from model.work import WorkModel
from ral.cache import checkCache, deleteCache
from ral.user import finishCntKey
from util.const import match
from util.const.base import ALL_STR
from util.const.match import MODEL_SEX_UNKNOWN_INDEX, MODEL_MARTIAL_STATUS_UNKNOWN, MODEL_MAIL_TYPE_UNKNOWN
from util.ctx import getDbSession


class UserModel(BaseModel):
    """用户信息"""
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)  # 自增
    passport_id = Column(Integer, default=0)  # passport_id
    sex = Column(Integer, default=MODEL_SEX_UNKNOWN_INDEX)  # 性别：MODEL_SEX_ENUMERATE
    birth_year = Column(Integer, default=0)  # 出生年份
    height = Column(Integer, default=0)  # 身高(厘米)
    weight = Column(Integer, default=0)  # 体重(公斤)
    home_region_id = Column(Integer, default=0)  # 籍贯地点id
    study_from_year = Column(Integer, default=0)  # 入学年份
    # 学习信息
    study_region_id = Column(Integer, default=0)  # 学习地点id
    school_id = Column(Integer, default=0)  # 学校id
    education_level = Column(Integer, default=0)  # 学历：EDUCATION_LEVEL
    education_id = Column(Integer, default=0)  # 学习信息id
    # 工作信息
    work_region_id = Column(Integer, default=0)  # 工作地点id
    company_id = Column(Integer, default=0)  # 公司id
    work_id = Column(Integer, default=0)  # 工作信息id
    # 婚姻
    martial_status = Column(Integer, default=MODEL_MARTIAL_STATUS_UNKNOWN)  # 婚姻现状：MODEL_MARTIAL_STATUS_ENUMERATE
    month_pay = Column(Integer, default=0)  # 月收入(元)
    is_fall_in_love = Column(Integer, default=0)  # 是否坠入爱河
    info_has_filled = Column(Integer, default=0)  # 是否完善信息：0否，1是
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    @checkCache("UserModel:{passportId}")
    def getByPassportId(cls, passportId):
        return getDbSession().query(cls).filter(cls.passport_id == passportId, cls.status == match.MODEL_STATUS_YES).first()

    @classmethod
    def getByPassportIds(cls, passportIds):
        return getDbSession().query(cls).filter(cls.passport_id.in_(passportIds), cls.status == match.MODEL_STATUS_YES)

    @classmethod
    def addByPassportId(cls, passportId):
        user = cls(
            passport_id=passportId,
            status=match.MODEL_STATUS_YES
        )
        getDbSession().add(user)
        getDbSession().flush()
        return user

    @classmethod
    @deleteCache(["UserModel:{passportId}"])
    def updateByPassportId(cls, passportId=0, **updateParams):
        getDbSession().query(cls).filter(cls.passport_id == passportId, cls.status == match.MODEL_STATUS_YES).update(updateParams)
        getDbSession().commit()

    @classmethod
    @checkCache(finishCntKey)
    def getFillFinishCnt(cls):
        return getDbSession().query(cls.id).filter(cls.info_has_filled == match.MODEL_STATUS_YES).count()

    @property
    def verify_type(self):
        verify = VerifyModel.getByPassportId(self.passport_id)
        return verify.mail_type if verify else MODEL_MAIL_TYPE_UNKNOWN

    @property
    def sexIndex(self):
        return self.sex

    @property
    def home_region(self):
        """home_address_id"""
        return RegionModel.getById(self.home_region_id)

    @property
    def home_province(self):
        return self.home_region.province if self.home_region else ALL_STR

    @property
    def home_city(self):
        return self.home_region.city if self.home_region else ALL_STR

    @property
    def home_area(self):
        return self.home_region.area if self.home_region else ALL_STR

    @property
    def study_region(self):
        return RegionModel.getById(self.study_region_id)

    @property
    def study_province(self):
        return self.study_region.province if self.study_region else ALL_STR

    @property
    def study_city(self):
        return self.study_region.city if self.study_region else ALL_STR

    @property
    def study_area(self):
        return self.study_region.area if self.study_region else ALL_STR

    @property
    def education(self):
        return EducationModel.getById(self.education_id)

    @property
    def school(self):
        return self.education.school if self.education else ALL_STR

    @property
    def level(self):
        return self.education.level if self.education else ALL_STR

    @property
    def major(self):
        return self.education.major if self.education else ALL_STR

    @property
    def work(self):
        return WorkModel.getById(self.work_id)

    @property
    def profession(self):
        return self.work.profession if self.work else ALL_STR

    @property
    def industry(self):
        return self.work.industry if self.work else ALL_STR

    @property
    def position(self):
        return self.work.position if self.work else ALL_STR

    @property
    def work_region(self):
        """home_address_id"""
        return RegionModel.getById(self.work_region_id)

    @property
    def work_province(self):
        return self.work_region.province if self.work_region else ALL_STR

    @property
    def work_city(self):
        return self.work_region.city if self.work_region else ALL_STR

    @property
    def work_area(self):
        return self.work_region.area if self.work_region else ALL_STR
