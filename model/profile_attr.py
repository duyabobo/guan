#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import LargeBinary
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from service.identity.runtime_key import material_for, materials_for
from util.const import match
from util.const.identity import PURPOSE_PROFILE
from util.ctx import getDbSession
from util.sensitive_cipher import open_json, seal_json

logger = logging.getLogger(__name__)


class ProfileAttrModel(BaseModel):
    """个人资料与个人期望。一个用户、一个范围、一个维度对应一行。"""
    __tablename__ = 'profile_attr'
    id = Column(Integer, primary_key=True)
    passport_id = Column(Integer, default=0)
    scope = Column(String(16), default='')  # info / requirement
    dim_key = Column(String(64), default='')
    value_text = Column(String(512), default='')  # 不再写入明文，保留列只为清空旧数据
    value_min = Column(Integer, default=0)  # 单值，或区间下限。明文不再使用
    value_max = Column(Integer, default=0)  # 区间上限。明文不再使用
    value_nonce = Column(String(32), default='')
    value_cipher = Column(LargeBinary)
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @classmethod
    def listByPassportId(cls, passport_id):
        if not passport_id:
            return []
        return cls.listByPassportIds([passport_id])

    @classmethod
    def listByPassportIds(cls, passport_ids):
        ids = [passport_id for passport_id in passport_ids if passport_id]
        if not ids:
            return []
        rows = getDbSession().query(cls).filter(
            cls.passport_id.in_(ids),
            cls.status == match.MODEL_STATUS_YES,
        ).all()
        return _opened_values(rows, materials_for(ids, PURPOSE_PROFILE))

    @classmethod
    def saveScope(cls, passport_id, scope, values_by_key):
        """按维度覆盖写入。先一次查出已有行，再在内存里改，避免循环里查库。"""
        if not passport_id or not values_by_key:
            return True
        material = material_for(passport_id, PURPOSE_PROFILE)
        if not material:
            logger.error("资料未写入，运行时没有身份密钥 passport=%s", passport_id)
            return False
        sealed = _seal_values(material, values_by_key)
        if sealed is None:
            return False
        session = getDbSession()
        existing = session.query(cls).filter(
            cls.passport_id == passport_id,
            cls.scope == scope,
            cls.dim_key.in_(list(sealed.keys())),
        ).all()
        by_key = {row.dim_key: row for row in existing}
        for dim_key, packed in sealed.items():
            _apply_sealed(session, by_key.get(dim_key), passport_id, scope, dim_key, packed)
        session.commit()
        logger.info("profile_attr sealed passport=%s scope=%s dims=%s",
                    passport_id, scope, list(sealed.keys()))
        return True


class ProfileValue(object):

    def __init__(self, passport_id, scope, dim_key, value_min, value_max, value_text):
        self.passport_id = passport_id
        self.scope = scope
        self.dim_key = dim_key
        self.value_min = value_min
        self.value_max = value_max
        self.value_text = value_text


def _opened_values(rows, materials):
    session = getDbSession()
    opened = []
    for row in rows:
        value = _open_row(row, materials.get(row.passport_id, ''))
        if value is not None:
            opened.append(value)
        session.expunge(row)
    return opened


def _open_row(row, material):
    if row.value_cipher:
        return _open_cipher(row, material)
    if _legacy_plaintext(row):
        logger.error("资料仍是明文，拒绝读出 passport=%s dim=%s", row.passport_id, row.dim_key)
    return None


def _open_cipher(row, material):
    if not material:
        logger.info("资料解不开，运行时没有身份密钥 passport=%s dim=%s", row.passport_id, row.dim_key)
        return None
    try:
        payload = open_json(material, row.value_nonce, row.value_cipher)
    except (ValueError, UnicodeDecodeError):
        logger.error("资料解密失败 passport=%s dim=%s", row.passport_id, row.dim_key)
        return None
    return ProfileValue(
        row.passport_id,
        row.scope,
        row.dim_key,
        int(payload.get('value_min') or 0),
        int(payload.get('value_max') or 0),
        str(payload.get('value_text') or ''),
    )


def _legacy_plaintext(row):
    return bool((row.value_text or '').strip() or row.value_min or row.value_max)


def _seal_values(material, values_by_key):
    sealed = {}
    for dim_key, value in values_by_key.items():
        try:
            nonce, cipher = seal_json(material, value)
        except ValueError:
            logger.error("资料加密失败 dim=%s", dim_key)
            return None
        sealed[dim_key] = (nonce, cipher)
    return sealed


def _apply_sealed(session, row, passport_id, scope, dim_key, packed):
    nonce, cipher = packed
    if row is None:
        session.add(ProfileAttrModel(
            passport_id=passport_id,
            scope=scope,
            dim_key=dim_key,
            value_min=0,
            value_max=0,
            value_text='',
            value_nonce=nonce,
            value_cipher=cipher,
            status=match.MODEL_STATUS_YES,
        ))
        return
    row.value_min = 0
    row.value_max = 0
    row.value_text = ''
    row.value_nonce = nonce
    row.value_cipher = cipher
    row.status = match.MODEL_STATUS_YES
