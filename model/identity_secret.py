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
from util.sensitive_cipher import seal_unionid, stored_unionid_accepts, union_lookup

logger = logging.getLogger(__name__)


class IdentitySecretModel(BaseModel):
    """身份密钥。登录时覆盖写入。业务查询不要读这张表。"""

    __tablename__ = 'identity_secret'
    id = Column(Integer, primary_key=True)
    passport_id = Column(Integer, default=0)
    provider = Column(String(32), default='')
    account_key = Column(String(64), default='')
    secret_material = Column(String(512), default='')  # unionid 用自己加密后的封存值，不是明文
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

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
    def accepts(cls, passport_id, provider, unionid):
        """已封存的密钥必须和这次微信返回的 unionid 是同一把。"""
        if not passport_id or not provider or not unionid:
            return False
        row = getDbSession().query(cls.secret_material).filter(
            cls.passport_id == passport_id,
            cls.provider == provider,
            cls.status == match.MODEL_STATUS_YES,
        ).first()
        if not row or not row[0]:
            return True
        if stored_unionid_accepts(row[0], unionid):
            return True
        logger.error("登录身份密钥和已封存的不一致 passport=%s provider=%s", passport_id, provider)
        return False

    @classmethod
    def save_sealed(cls, passport_id, provider, unionid):
        """只写查找值和自加密封存。明文 unionid 不入库。"""
        if not passport_id or not provider or not unionid:
            logger.error("拒绝保存空的身份密钥 passport=%s provider=%s", passport_id, provider)
            return False
        if not cls.accepts(passport_id, provider, unionid):
            return False
        session = getDbSession()
        account_key = union_lookup(unionid)
        sealed = seal_unionid(unionid)
        existing = session.query(cls.id).filter(
            cls.passport_id == passport_id,
            cls.provider == provider,
            cls.status == match.MODEL_STATUS_YES,
        ).first()
        if existing:
            session.query(cls).filter(cls.id == existing[0]).update({
                cls.account_key: account_key,
                cls.secret_material: sealed,
            }, synchronize_session=False)
            logger.info("已更新身份密钥封存 passport=%s provider=%s", passport_id, provider)
            return True
        session.add(cls(
            passport_id=passport_id,
            provider=provider,
            account_key=account_key,
            secret_material=sealed,
            status=match.MODEL_STATUS_YES,
        ))
        session.flush()
        logger.info("已写入身份密钥封存 passport=%s provider=%s", passport_id, provider)
        return True
