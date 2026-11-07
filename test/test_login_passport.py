#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""登录找回、分享绑定和手机号密文。不连真实数据库。"""
from service.identity.assertion import IdentityAssertion
from service.identity.runtime_key import unique_passport_ids
from service.login import LoginService
from service.meet_seat import take_seat_updates
from service.phone_bind import PhoneBindService
from service import phone_bind
from util.const.identity import PROVIDER_NATIONAL_NETWORK, PROVIDER_WECHAT, RUNTIME_UNION_KEY
from util.redis_conn import decode_redis_value, redisConn
from util.sensitive_cipher import open_phone, open_phone_or_none, open_text_or_none, seal_bytes_or_none, union_lookup


class _Passport(object):

    def __init__(self, passport_id):
        self.id = passport_id


def _assertion(material='union-secret', openid='openid-1', provider=PROVIDER_WECHAT):
    return IdentityAssertion(provider, openid, material)


def _patch_login(monkeypatch, by_key, created, shares, bound=False, known_ids=()):
    import service.login as login_mod

    def get_by_union_key(union_key):
        return by_key.get(union_key)

    def add_with_union_key(union_key):
        passport = _Passport(8 + len(created))
        created.append((union_key, passport.id))
        by_key[union_key] = passport
        return passport

    def get_by_id(passport_id):
        if passport_id in known_ids:
            return _Passport(passport_id)
        return None

    monkeypatch.setattr(login_mod.PassportModel, 'get_by_union_key', staticmethod(get_by_union_key))
    monkeypatch.setattr(login_mod.PassportModel, 'add_with_union_key', staticmethod(add_with_union_key))
    monkeypatch.setattr(login_mod.PassportModel, 'getById', staticmethod(get_by_id))
    monkeypatch.setattr(login_mod.ShareModel, 'addOne', staticmethod(lambda sharer, accept: shares.append((sharer, accept))))
    monkeypatch.setattr(login_mod, 'seal_passport_plaintext', lambda passport_id, unionid: None)
    monkeypatch.setattr(login_mod.PhoneBindService, 'bound', lambda self, passport_id: bound)


def test_existing_union_key_reuses_passport_and_keeps_plain_unionid_in_redis(monkeypatch):
    existing = _Passport(7)
    by_key = {union_lookup('union-secret'): existing}
    created = []
    shares = []
    _patch_login(monkeypatch, by_key, created, shares, bound=True)
    logged = LoginService().login(_assertion(), share_passport_id=3)
    assert logged[2] == 'openid-1'
    assert logged[3] is True
    assert logged[4] == 7
    assert created == []
    assert shares == []
    stored = decode_redis_value(redisConn.get(RUNTIME_UNION_KEY % 7))
    assert stored == 'union-secret'
    assert union_lookup('union-secret') not in stored


def test_new_login_stores_lookup_key_and_records_share(monkeypatch):
    by_key = {}
    created = []
    shares = []
    _patch_login(monkeypatch, by_key, created, shares, known_ids={3})
    logged = LoginService().login(_assertion(), share_passport_id=3)
    union_key, passport_id = created[0]
    assert union_key == union_lookup('union-secret')
    assert 'union-secret' not in union_key
    assert logged[4] == passport_id
    assert shares == [(3, passport_id)]


def test_new_login_skips_share_of_self_or_unknown(monkeypatch):
    by_key = {}
    created = []
    shares = []
    _patch_login(monkeypatch, by_key, created, shares)
    logged = LoginService().login(_assertion(material='union-a'), share_passport_id=8)
    assert logged[4] == 8
    LoginService().login(_assertion(material='union-b'), share_passport_id=99)
    other = LoginService().login(
        _assertion(material='union-c', openid='openid-c', provider=PROVIDER_NATIONAL_NETWORK),
        share_passport_id=0,
    )
    assert shares == []
    assert other[2] == ''


def test_login_without_secret_material_does_not_create_passport(monkeypatch):
    created = []
    _patch_login(monkeypatch, {}, created, [])
    assert LoginService().login(_assertion(material=''), 0) is None
    assert created == []


def test_phone_bind_writes_cipher_and_bound_reads_it(monkeypatch):
    saved = {}

    from service.phone_code import PhoneCodeService
    monkeypatch.setattr(
        PhoneCodeService, 'take',
        lambda self, passport_id, phone, code: '13800138000' if code == '123456' else '',
    )
    monkeypatch.setattr(phone_bind, 'material_for', lambda passport_id, purpose: 'union-secret')
    monkeypatch.setattr(phone_bind.PassportModel, 'save_phone', staticmethod(lambda passport_id, sealed: saved.update({passport_id: sealed}) or True))
    monkeypatch.setattr(phone_bind.PassportModel, 'phone_cipher', staticmethod(lambda passport_id: saved.get(passport_id, '')))

    service = PhoneBindService()
    assert service.bind(7, '13800138000', '000000') is False
    assert service.bind(7, '13800138000', '123456') is True
    sealed = saved[7]
    assert '13800138000' not in sealed
    assert open_phone('union-secret', sealed) == '13800138000'
    assert service.bound(7) is True
    assert service.bound(0) is False

    monkeypatch.setattr(phone_bind, 'material_for', lambda passport_id, purpose: '')
    assert service.bind(7, '13800138000', '123456') is False


def test_unique_passport_ids_drop_empty_and_duplicates():
    assert unique_passport_ids([0, 1, '1', None, 2, 2]) == [1, 2]
    assert unique_passport_ids([]) == []


def test_runtime_seal_helpers_reject_missing_material_and_wrong_key():
    packed = seal_bytes_or_none('union-a', b'openid-plain')
    assert packed is not None
    nonce, cipher = packed
    assert open_text_or_none('union-a', nonce, cipher) == 'openid-plain'
    assert open_text_or_none('union-b', nonce, cipher) is None
    assert seal_bytes_or_none('', b'openid-plain') is None
    assert open_phone_or_none('', 'not-a-seal') is None


def test_seat_update_removes_passport_ids_from_activity_row():
    params = {'state': 1, 'boy_passport_id': 7, 'girl_passport_id': 0}
    changes = take_seat_updates(params)
    assert changes
    assert params['boy_passport_id'] == 0
    assert params['girl_passport_id'] == 0
    assert params['state'] == 1
    assert 7 in changes.values()
