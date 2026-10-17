#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from model.profile_attr import ProfileAttrModel
from service.common.profile_catalog import (
    FILL_REQUIRED_INFO_KEYS,
    SCOPE_INFO,
    values_from_payload,
)
from service.common.profile_rows import build_rows

logger = logging.getLogger(__name__)


class ProfileBoardService(object):
    """见面详情和个人信息页共用的资料板。值只来自 profile_attr。"""

    @staticmethod
    def rows_for(passport_id):
        attr_rows = ProfileAttrModel.listByPassportId(passport_id)
        rows = build_rows(attr_rows)
        logger.info("profile board passport=%s dims=%s", passport_id, [row["dimKey"] for row in rows])
        return rows

    @staticmethod
    def save_extracted(passport_id, scope, payload):
        values = values_from_payload(scope, payload)
        ProfileAttrModel.saveScope(passport_id, scope, values)

    @staticmethod
    def sex_of(passport_id):
        row = _info_row(passport_id, "sex")
        if row is None:
            return 0
        return row.value_min or 0

    @staticmethod
    def info_is_filled(passport_id):
        rows = _info_map(passport_id)
        for key in FILL_REQUIRED_INFO_KEYS:
            row = rows.get(key)
            if row is None or not row.value_min:
                return False
        return True


def _info_map(passport_id):
    rows = ProfileAttrModel.listByPassportId(passport_id)
    return {row.dim_key: row for row in rows if row.scope == SCOPE_INFO}


def _info_row(passport_id, dim_key):
    return _info_map(passport_id).get(dim_key)
