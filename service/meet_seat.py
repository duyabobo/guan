#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""见面座位的读写。库里不出现护照编号和场次编号的明文对应。"""
import logging

from sqlalchemy.orm.attributes import set_committed_value

from model.activity_seat import ActivitySeatModel
from service.identity.runtime_key import material_for, materials_for
from util.const.identity import PURPOSE_MEET_SEAT
from util.const.match import MODEL_SEX_FEMALE_INDEX, MODEL_SEX_MALE_INDEX
from util.sensitive_cipher import open_json, seal_json
from util.slot_blind import activity_slot_key

logger = logging.getLogger(__name__)

SEAT_BOY = MODEL_SEX_MALE_INDEX
SEAT_GIRL = MODEL_SEX_FEMALE_INDEX
_SEAT_ROLES = (SEAT_BOY, SEAT_GIRL)
_FIELD_ROLE = {
    'boy_passport_id': SEAT_BOY,
    'girl_passport_id': SEAT_GIRL,
}


def take_seat_updates(update_params):
    """从活动更新参数里拿走护照编号，改由座位密文保存。"""
    changes = {}
    for field, role in _FIELD_ROLE.items():
        if field in update_params:
            changes[role] = int(update_params.pop(field) or 0)
    if changes:
        update_params['boy_passport_id'] = 0
        update_params['girl_passport_id'] = 0
    return changes


def apply_seat_changes(activity_id, role_to_passport):
    if not role_to_passport:
        return True
    slot = activity_slot_key(activity_id)
    if not slot:
        logger.error("座位未写入，盲索引为空 activity=%s", activity_id)
        return False
    for role, passport_id in role_to_passport.items():
        if passport_id:
            if not _remember(passport_id, slot, activity_id, role):
                return False
        elif not _forget_role(slot, role):
            return False
    return True


def activity_ids_of(passport_id):
    material = material_for(passport_id, PURPOSE_MEET_SEAT)
    if not passport_id or not material:
        if passport_id:
            logger.info("查不到本人的见面，运行时没有身份密钥 passport=%s", passport_id)
        return []
    found = []
    for row in ActivitySeatModel.list_by_passport(passport_id):
        payload = _open_seat(row, material)
        activity_id = int(payload.get('activity_id') or 0) if payload else 0
        if activity_id:
            found.append(activity_id)
    return found


def fill_occupants(activities):
    """把座位解到内存里的活动对象上，不把护照编号写回数据库。"""
    rows = [activity for activity in activities or [] if getattr(activity, 'id', None)]
    if not rows:
        return
    seated, locked = occupants_of([activity.id for activity in rows])
    for activity in rows:
        seats = seated.get(activity.id, {})
        set_committed_value(activity, 'boy_passport_id', seats.get(SEAT_BOY, 0))
        set_committed_value(activity, 'girl_passport_id', seats.get(SEAT_GIRL, 0))
        activity.seat_locked = activity.id in locked


def occupants_of(activity_ids):
    slot_of = _slot_map(activity_ids)
    if not slot_of:
        return {}
    rows = ActivitySeatModel.list_by_slots(list(slot_of.keys()))
    materials = materials_for([row.passport_id for row in rows], PURPOSE_MEET_SEAT)
    seated = {}
    locked = set()
    for row in rows:
        activity_id = slot_of.get(row.slot_key, 0)
        payload = _open_seat(row, materials.get(row.passport_id, ''))
        if payload is None:
            if activity_id:
                locked.add(activity_id)
            continue
        _place(seated, activity_id, row.passport_id, payload)
    return seated, locked


def _remember(passport_id, slot, activity_id, role):
    material = material_for(passport_id, PURPOSE_MEET_SEAT)
    if not material:
        logger.error("座位未写入，运行时没有身份密钥 passport=%s activity=%s", passport_id, activity_id)
        return False
    try:
        nonce, cipher = seal_json(material, {'activity_id': int(activity_id), 'role': int(role)})
    except ValueError:
        logger.error("座位加密失败 passport=%s activity=%s", passport_id, activity_id)
        return False
    ActivitySeatModel.save_seat(passport_id, slot, nonce, cipher)
    return True


def _forget_role(slot, role):
    rows = ActivitySeatModel.list_by_slots([slot])
    materials = materials_for([row.passport_id for row in rows], PURPOSE_MEET_SEAT)
    cleared = False
    locked = False
    for row in rows:
        payload = _open_seat(row, materials.get(row.passport_id, ''))
        if payload is None:
            locked = True
            continue
        if int(payload.get('role') or 0) != int(role):
            continue
        ActivitySeatModel.clear_passport(row.passport_id, slot)
        cleared = True
    if cleared or not locked:
        return True
    logger.error("席位没清掉，身份密钥不在运行时")
    return False


def _slot_map(activity_ids):
    found = {}
    for activity_id in activity_ids or []:
        if not activity_id:
            continue
        slot = activity_slot_key(activity_id)
        if slot:
            found[slot] = int(activity_id)
    return found


def _open_seat(row, material):
    if not material or not row.cipher_text:
        logger.info("座位解不开 passport=%s", row.passport_id)
        return None
    try:
        payload = open_json(material, row.nonce, row.cipher_text)
    except (ValueError, UnicodeDecodeError):
        logger.error("座位解密失败 passport=%s", row.passport_id)
        return None
    role = int(payload.get('role') or 0)
    if role not in _SEAT_ROLES:
        logger.error("座位角色无效 passport=%s", row.passport_id)
        return None
    return payload


def _place(seated, activity_id, passport_id, payload):
    if not activity_id or not payload:
        return
    role = int(payload.get('role') or 0)
    seated.setdefault(activity_id, {})[role] = int(passport_id)
