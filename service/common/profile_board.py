#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from model.profile_attr import ProfileAttrModel
from service.common.profile_catalog import SCOPE_INFO
from service.common.profile_rows import build_rows, missing_required_info_keys

logger = logging.getLogger(__name__)


class ProfileBoardService(object):
    """见面详情和个人信息页共用的资料板。值只来自 profile_attr。"""

    @staticmethod
    def rows_for(passport_id, show_all=False):
        attr_rows = ProfileAttrModel.listByPassportId(passport_id)
        rows = build_rows(attr_rows, show_all=show_all)
        logger.info("profile board passport=%s dims=%s show_all=%s", passport_id, [row["dimKey"] for row in rows], show_all)
        return rows

    @staticmethod
    def save_packed(passport_id, scope, values):
        if not passport_id or not values:
            return
        ProfileAttrModel.saveScope(passport_id, scope, values)
        logger.info("profile_attr scope=%s passport=%s dims=%s", scope, passport_id, list(values.keys()))

    @staticmethod
    def sex_of(passport_id):
        row = _info_row(passport_id, "sex")
        if row is None:
            return 0
        return row.value_min or 0

    @staticmethod
    def info_is_filled(passport_id):
        missing = missing_required_info_keys(_info_map(passport_id))
        if missing:
            logger.info("个人信息未齐 passport=%s missing=%s", passport_id, missing)
            return False
        return True


def _info_map(passport_id):
    rows = ProfileAttrModel.listByPassportId(passport_id)
    return {row.dim_key: row for row in rows if row.scope == SCOPE_INFO}


def _info_row(passport_id, dim_key):
    return _info_map(passport_id).get(dim_key)
