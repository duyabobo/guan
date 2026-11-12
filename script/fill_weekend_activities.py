#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""每天补一次全国主要城市的周末上午活动。

只补周六、周日 9:00 到 12:00（含 12:00），每半小时一场。
已经有同一地点、同一开始时间的有效场次就跳过。
"""
import datetime
import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(current_dir))

from sqlalchemy import bindparam, text

from script.major_cities import MAJOR_CITY_VENUES, region_key
from service.weekend_activity_supply import (
    SUPPLY_LOOKAHEAD_DAYS,
    activities_to_add,
    weekend_slot_times,
)
from util.const.base import EMPTY_STR
from util.const.match import MODEL_ACTIVITY_STATE_EMPTY, MODEL_STATUS_YES
from util.database import SessionFactory
from util.log import offline_script_logger


VENUE_DESC = "周末上午见面"
_REGION_ROWS = text("SELECT id, province, city, area FROM region WHERE status = :status")
_ADDRESS_ROWS = text(
    "SELECT id, name FROM address WHERE status = :status AND name IN :names"
).bindparams(bindparam("names", expanding=True))
_ACTIVITY_ROWS = text(
    """
    SELECT address_id, start_time FROM activity
    WHERE status = :status
      AND address_id IN :address_ids
      AND start_time >= :start_time
      AND start_time <= :end_time
    """
).bindparams(bindparam("address_ids", expanding=True))

logger = offline_script_logger("fill_weekend_activities")


def fill_weekend_activities(session, now=None):
    now = now or datetime.datetime.now().replace(second=0, microsecond=0)
    slots = weekend_slot_times(now)
    region_ids = _ensure_regions(session)
    address_ids = _ensure_addresses(session, region_ids)
    address_id_list = list(address_ids.values())
    existing = _existing_keys(session, address_id_list, slots)
    missing = activities_to_add(address_id_list, slots, existing)
    _insert_activities(session, missing)
    logger.info(
        "周末活动供给完成 城市=%s 时段=%s 新场次=%s 展望天数=%s",
        len(MAJOR_CITY_VENUES), len(slots), len(missing), SUPPLY_LOOKAHEAD_DAYS,
    )
    return len(missing)


def _ensure_regions(session):
    found = _region_ids(session)
    missing = [venue for venue in MAJOR_CITY_VENUES if region_key(venue) not in found]
    if missing:
        session.execute(text(
            """
            INSERT INTO region (province, city, area, status)
            VALUES (:province, :city, :area, :status)
            """
        ), [
            {
                "province": venue.province,
                "city": venue.city,
                "area": venue.area,
                "status": MODEL_STATUS_YES,
            }
            for venue in missing
        ])
        found = _region_ids(session)
    absent = [venue.city for venue in MAJOR_CITY_VENUES if region_key(venue) not in found]
    if absent:
        raise RuntimeError("省市区没有写上: %s" % "、".join(absent))
    logger.info("省市区已齐 新增=%s 总数=%s", len(missing), len(MAJOR_CITY_VENUES))
    return {region_key(venue): found[region_key(venue)] for venue in MAJOR_CITY_VENUES}


def _region_ids(session):
    rows = session.execute(_REGION_ROWS, {"status": MODEL_STATUS_YES}).fetchall()
    return {(row.province, row.city, row.area): row.id for row in rows}


def _ensure_addresses(session, region_ids):
    found = _address_ids(session)
    missing = [venue for venue in MAJOR_CITY_VENUES if venue.name not in found]
    if missing:
        session.execute(text(
            """
            INSERT INTO address
                (name, description, region_id, longitude, latitude, img_obj_name, status)
            VALUES
                (:name, :description, :region_id, :longitude, :latitude, :img_obj_name, :status)
            """
        ), [_address_params(venue, region_ids) for venue in missing])
        found = _address_ids(session)
    absent = [venue.name for venue in MAJOR_CITY_VENUES if venue.name not in found]
    if absent:
        raise RuntimeError("见面点没有写上: %s" % "、".join(absent))
    logger.info("见面点已齐 新增=%s 总数=%s", len(missing), len(found))
    return found


def _address_ids(session):
    rows = session.execute(_ADDRESS_ROWS, {
        "status": MODEL_STATUS_YES,
        "names": [venue.name for venue in MAJOR_CITY_VENUES],
    }).fetchall()
    return {row.name: row.id for row in rows}


def _address_params(venue, region_ids):
    return {
        "name": venue.name,
        "description": VENUE_DESC,
        "region_id": region_ids[region_key(venue)],
        "longitude": venue.longitude,
        "latitude": venue.latitude,
        "img_obj_name": EMPTY_STR,
        "status": MODEL_STATUS_YES,
    }


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


def main():
    with SessionFactory() as session:
        fill_weekend_activities(session)
        session.commit()


if __name__ == "__main__":
    main()
