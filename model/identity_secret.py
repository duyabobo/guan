#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util.const import match
from util.ctx import getDbSession
from util.encode import md5_hex

logger = logging.getLogger(__name__)


class IdentitySecretModel(BaseModel):
    """身份密钥。登录时覆盖写入。业务查询不要读这张表。"""

    __tablename__ = 'identity_secret'
    id = Column(Integer, primary_key=True)
    passport_id = Column(Integer, default=0)
    provider = Column(String(32), default='')
    account_key = Column(String(64), default='')
    secret_material = Column(String(512), default='')
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @staticmethod
    def account_key_of(account_key_raw):
        return md5_hex(account_key_raw)

    @classmethod
    def passport_id_of(cls, provider, account_key_hash):
        """只返回通行证编号，不读取密钥材料。"""
        if not provider or not account_key_hash:
            return 0
        row = getDbSession().query(cls.passport_id).filter(
            cls.provider == provider,
            cls.account_key == account_key_hash,
            cls.status == match.MODEL_STATUS_YES,
        ).first()
        if not row:
            return 0
        return int(row[0])

    @classmethod
    def save_material(cls, passport_id, provider, account_key_raw, secret_material):
        if not passport_id or not provider or not account_key_raw or not secret_material:
            logger.error("拒绝保存空的身份密钥 passport=%s provider=%s", passport_id, provider)
            return None
        session = getDbSession()
        account_key = cls.account_key_of(account_key_raw)
        existing = session.query(cls.id).filter(
            cls.passport_id == passport_id,
            cls.provider == provider,
            cls.status == match.MODEL_STATUS_YES,
        ).first()
        if existing:
            session.query(cls).filter(cls.id == existing[0]).update({
                cls.account_key: account_key,
                cls.secret_material: secret_material,
            }, synchronize_session=False)
            logger.info("已更新身份密钥 passport=%s provider=%s", passport_id, provider)
            return True
        session.add(cls(
            passport_id=passport_id,
            provider=provider,
            account_key=account_key,
            secret_material=secret_material,
            status=match.MODEL_STATUS_YES,
        ))
        session.flush()
        logger.info("已写入身份密钥 passport=%s provider=%s", passport_id, provider)
        return True

    @classmethod
    def load_for_sensitive_use(cls, passport_id, provider, purpose):
        """加密写入或最终核查时才读密钥。调用方必须带上用途。"""
        if not purpose:
            logger.error("拒绝无用途读取身份密钥 passport=%s provider=%s", passport_id, provider)
            return ''
        logger.info("读取身份密钥 passport=%s provider=%s purpose=%s", passport_id, provider, purpose)
        row = getDbSession().query(cls).filter(
            cls.passport_id == passport_id,
            cls.provider == provider,
            cls.status == match.MODEL_STATUS_YES,
        ).first()
        if not row or not row.secret_material:
            return ''
        material = row.secret_material
        getDbSession().expunge(row)
        return material

    @classmethod
    def load_materials(cls, passport_ids, provider, purpose):
        """批量读取。调用方必须带用途。一次查询，不在循环里逐个读。"""
        ids = [passport_id for passport_id in passport_ids if passport_id]
        if not purpose or not ids:
            logger.error("拒绝无用途或空列表读取身份密钥 provider=%s", provider)
            return {}
        logger.info("读取身份密钥 purpose=%s count=%s", purpose, len(ids))
        rows = getDbSession().query(cls).filter(
            cls.passport_id.in_(ids),
            cls.provider == provider,
            cls.status == match.MODEL_STATUS_YES,
        ).all()
        found = {}
        session = getDbSession()
        for row in rows:
            if row.secret_material:
                found[row.passport_id] = row.secret_material
            session.expunge(row)
        return found
