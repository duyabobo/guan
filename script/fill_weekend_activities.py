#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""每天补一次肯德基门店的周末上午活动。

每次只补「下一周六」9:00 到 12:00（含 12:00），每半小时一场。
本周六上午已全部过点则补再下一个周六。已有同地点同时段则跳过。
门店来自已导入的 OSM 肯德基地址（img_obj_name=address/brand/kfc.png）。
仅用名称含「肯德基/KFC」的地址；裸名会规范成「肯德基xx店」。
"""
import datetime
import os
import re
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(current_dir))

from sqlalchemy import bindparam, text

from service.weekend_activity_supply import (
    activities_to_add,
    weekend_slot_times,
)
from util.const.match import MODEL_ACTIVITY_STATE_EMPTY, MODEL_STATUS_NO, MODEL_STATUS_YES
from util.database import SessionFactory
from util.log import offline_script_logger


KFC_IMAGE = "address/brand/kfc.png"
KFC_NAME_ZH = "%肯德基%"
KFC_NAME_EN = "%KFC%"
MEETUP_POINT_NAME_SUFFIX = "%见面点"
DEFAULT_STORE_NAME = "肯德基门店"
BARE_KFC_NAMES = frozenset({"肯德基", "KFC", "肯德基 KFC", "kfc", DEFAULT_STORE_NAME})
NAME_LIMIT = 256
HINT_LIMIT = 32
_STREET_HINT = re.compile(r"[路街道巷大道里园广场]")
_ADMIN_ONLY = re.compile(r"^[\u4e00-\u9fff]+省\s*[\u4e00-\u9fff]+市$")
_CITY_ONLY = re.compile(r"^[\u4e00-\u9fff]+市(\s*[\u4e00-\u9fff]+市)?$")
_BAD_DERIVED_NAME = re.compile(r"未标注|市.+市店$")

_BRAND_ADDRESS_ROWS = text(
    """
    SELECT a.id, a.name, a.description, r.city, r.area
    FROM address a
    LEFT JOIN region r ON r.id = a.region_id
    WHERE a.status = :status
      AND a.img_obj_name = :img
      AND (a.name LIKE :kfc_zh OR UPPER(a.name) LIKE :kfc_en)
    ORDER BY a.id
    """
)
_RENAME_ADDRESS = text("UPDATE address SET name = :name WHERE id = :id AND status = :status")
_ACTIVITY_ROWS = text(
    """
    SELECT address_id, start_time FROM activity
    WHERE status = :status
      AND address_id IN :address_ids
      AND start_time >= :start_time
      AND start_time <= :end_time
    """
).bindparams(bindparam("address_ids", expanding=True))
_RETIRE_MEETUP_SLOTS = text(
    """
    UPDATE activity act
    INNER JOIN address a ON a.id = act.address_id
    SET act.status = :status_no
    WHERE act.status = :status_yes
      AND act.state = :empty_state
      AND a.name LIKE :meetup_name
    """
)
_RETIRE_NON_KFC_SLOTS = text(
    """
    UPDATE activity act
    INNER JOIN address a ON a.id = act.address_id
    SET act.status = :status_no
    WHERE act.status = :status_yes
      AND act.state = :empty_state
      AND a.img_obj_name = :img
      AND a.name NOT LIKE :kfc_zh
      AND UPPER(a.name) NOT LIKE :kfc_en
    """
)

logger = offline_script_logger("fill_weekend_activities")


def fill_weekend_activities(session, now=None):
    now = now or datetime.datetime.now().replace(second=0, microsecond=0)
    slots = weekend_slot_times(now)
    retired_meetup = _retire_empty(session, _RETIRE_MEETUP_SLOTS, {
        "status_no": MODEL_STATUS_NO,
        "status_yes": MODEL_STATUS_YES,
        "empty_state": MODEL_ACTIVITY_STATE_EMPTY,
        "meetup_name": MEETUP_POINT_NAME_SUFFIX,
    })
    retired_other = _retire_empty(session, _RETIRE_NON_KFC_SLOTS, {
        "status_no": MODEL_STATUS_NO,
        "status_yes": MODEL_STATUS_YES,
        "empty_state": MODEL_ACTIVITY_STATE_EMPTY,
        "img": KFC_IMAGE,
        "kfc_zh": KFC_NAME_ZH,
        "kfc_en": KFC_NAME_EN,
    })
    logger.info(
        "已下线空场次 meetup=%s non_kfc=%s",
        retired_meetup, retired_other,
    )
    address_ids = _prepare_kfc_addresses(session)
    if not address_ids:
        logger.error("没有可用的肯德基门店，请先导入 OSM 门店")
        return 0
    existing = _existing_keys(session, address_ids, slots)
    missing = activities_to_add(address_ids, slots, existing)
    _insert_activities(session, missing)
    saturday = slots[0].date() if slots else None
    logger.info(
        "周末活动供给完成 肯德基门店=%s 下一周六=%s 时段=%s 新场次=%s",
        len(address_ids), saturday, len(slots), len(missing),
    )
    return len(missing)


def store_display_name(name, description="", city="", area=""):
    """把裸「肯德基」或劣质派生名规范成「肯德基xx店」。"""
    raw = (name or "").strip()
    if _keep_existing_store_name(raw):
        return raw[:NAME_LIMIT]
    hint = _branch_hint(description, city, area)
    if not hint:
        return DEFAULT_STORE_NAME
    return _with_kfc_store_suffix(hint)[:NAME_LIMIT]


def _keep_existing_store_name(name):
    if name in BARE_KFC_NAMES:
        return False
    if _BAD_DERIVED_NAME.search(name):
        return False
    return True


def _with_kfc_store_suffix(hint):
    if hint.startswith("肯德基"):
        return hint if hint.endswith("店") else f"{hint}店"
    return f"肯德基{hint}" if hint.endswith("店") else f"肯德基{hint}店"


def _prepare_kfc_addresses(session):
    rows = session.execute(_BRAND_ADDRESS_ROWS, {
        "status": MODEL_STATUS_YES,
        "img": KFC_IMAGE,
        "kfc_zh": KFC_NAME_ZH,
        "kfc_en": KFC_NAME_EN,
    }).fetchall()
    address_ids = []
    renames = []
    for row in rows:
        display = store_display_name(row.name, row.description, row.city, row.area)
        if display != row.name:
            renames.append({
                "id": row.id,
                "name": display,
                "status": MODEL_STATUS_YES,
            })
        address_ids.append(row.id)
    if renames:
        session.execute(_RENAME_ADDRESS, renames)
    return address_ids


def _branch_hint(description, city, area):
    desc = (description or "").strip()
    if desc and _usable_street_hint(desc):
        return _clip_hint(desc)
    area_text = _clean_admin(area)
    if area_text:
        return _clip_hint(area_text)
    city_text = _clean_admin(city)
    if city_text:
        if city_text.endswith("市") and len(city_text) > 1:
            city_text = city_text[:-1]
        return _clip_hint(city_text)
    return ""


def _clean_admin(value):
    text = (value or "").strip()
    if not text or "未标注" in text:
        return ""
    return text


def _usable_street_hint(description):
    if not description or "未标注" in description:
        return False
    if _ADMIN_ONLY.match(description) or _CITY_ONLY.match(description):
        return False
    if _STREET_HINT.search(description):
        return True
    return "省" not in description and "市" not in description


def _clip_hint(text):
    cleaned = re.sub(r"\s+", "", text.strip())
    return cleaned[:HINT_LIMIT]


def _retire_empty(session, statement, params):
    result = session.execute(statement, params)
    return _rowcount(result)


def _existing_keys(session, address_ids, slots):
    if not address_ids or not slots:
        return set()
    rows = session.execute(_ACTIVITY_ROWS, {
        "status": MODEL_STATUS_YES,
        "address_ids": list(address_ids),
        "start_time": min(slots),
        "end_time": max(slots),
    }).fetchall()
    wanted = set(slots)
    return {
        (row.address_id, _drop_seconds(row.start_time))
        for row in rows
        if _drop_seconds(row.start_time) in wanted
    }


def _insert_activities(session, missing):
    if not missing:
        return
    session.execute(text(
        """
        INSERT INTO activity (address_id, start_time, state, status)
        VALUES (:address_id, :start_time, :state, :status)
        """
    ), [
        {
            "address_id": address_id,
            "start_time": start_time,
            "state": MODEL_ACTIVITY_STATE_EMPTY,
            "status": MODEL_STATUS_YES,
        }
        for address_id, start_time in missing
    ])


def _drop_seconds(moment):
    return moment.replace(second=0, microsecond=0)


def _rowcount(result):
    if result is None or not hasattr(result, "rowcount"):
        return 0
    return result.rowcount or 0


def main():
    with SessionFactory() as session:
        fill_weekend_activities(session)
        session.commit()


if __name__ == "__main__":
    main()
