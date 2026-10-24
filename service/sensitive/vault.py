#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from model.sensitive_record import SensitiveRecordModel
from service.identity.runtime_key import material_for
from util.const.identity import ACTIVE_KEY_PROVIDER, PURPOSE_ENCRYPT_STORE, SENSITIVE_KINDS
from util.ctx import getDbSession
from util.sensitive_cipher import encrypt

logger = logging.getLogger(__name__)


class SealedRecord(object):

    def __init__(self, passport_id, kind, key_provider, nonce, cipher_text, content_type, plain_length):
        self.passport_id = passport_id
        self.kind = kind
        self.key_provider = key_provider
        self.nonce = nonce
        self.cipher_text = cipher_text
        self.content_type = content_type
        self.plain_length = plain_length


class SensitiveVault(object):
    """加密写入。解密不在这里，避免业务链路顺手把原文解出来。"""

    def store(self, passport_id, kind, plain, content_type):
        sealed = self.seal(passport_id, kind, plain, content_type)
        if not sealed:
            return None
        return self.keep(sealed)

    def seal(self, passport_id, kind, plain, content_type):
        if kind not in SENSITIVE_KINDS:
            logger.error("未知敏感信息类型 %s", kind)
            return None
        if not passport_id or not plain:
            logger.warning("敏感信息缺少用户或内容 passport=%s kind=%s", passport_id, kind)
            return None
        material = material_for(passport_id, PURPOSE_ENCRYPT_STORE)
        if not material:
            logger.error("加密时没有身份密钥 passport=%s kind=%s", passport_id, kind)
            return None
        nonce, cipher_text = encrypt(material, plain)
        return SealedRecord(
            passport_id, kind, ACTIVE_KEY_PROVIDER, nonce, cipher_text, content_type, len(plain),
        )

    def release_read(self):
        """外网识别前结束只读事务，把数据库连接还回去。"""
        getDbSession().commit()
        logger.info("身份密钥读取结束，已释放数据库事务")

    def keep(self, sealed):
        row = SensitiveRecordModel.add(
            passport_id=sealed.passport_id,
            kind=sealed.kind,
            key_provider=sealed.key_provider,
            nonce=sealed.nonce,
            cipher_text=sealed.cipher_text,
            content_type=sealed.content_type,
            plain_length=sealed.plain_length,
        )
        return row.id
