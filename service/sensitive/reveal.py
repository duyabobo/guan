#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""最终核查才解密。产品页面不要调用。"""
import logging

from model.sensitive_record import SensitiveRecordModel
from service.identity.runtime_key import material_for
from service.sensitive.purpose import purpose_accepted
from util.sensitive_cipher import decrypt

logger = logging.getLogger(__name__)


class SensitiveReveal(object):

    def latest(self, passport_id, kind, purpose):
        if not purpose_accepted(purpose):
            logger.warning("最终核查被拒绝，用途无效 passport=%s kind=%s", passport_id, kind)
            return None
        record = SensitiveRecordModel.latest(passport_id, kind)
        if not record:
            logger.info("最终核查无记录 passport=%s kind=%s purpose=%s", passport_id, kind, purpose)
            return None
        return self._open(passport_id, record, purpose)

    def _open(self, passport_id, record, purpose):
        material = material_for(passport_id, purpose.strip())
        if not material:
            logger.error("最终核查缺少密钥 passport=%s record=%s", passport_id, record.id)
            return None
        try:
            plain = decrypt(material, record.nonce, record.cipher_text)
        except ValueError:
            logger.error("最终核查解密失败 passport=%s record=%s", passport_id, record.id)
            return None
        logger.warning(
            "已解密敏感信息 passport=%s kind=%s record=%s purpose=%s bytes=%s",
            passport_id, record.kind, record.id, purpose.strip(), len(plain),
        )
        return plain
