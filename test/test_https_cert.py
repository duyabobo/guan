#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os

import pytest

from util.https_cert import CERT_ENV, KEY_ENV, build_ssl_options


def _pair(directory):
    cert = directory / 'service.pem'
    key = directory / 'service.key'
    cert.write_text('cert')
    key.write_text('key')
    return cert, key


def test_ssl_options_reads_env_paths(tmp_path, monkeypatch):
    cert, key = _pair(tmp_path)
    monkeypatch.setenv(CERT_ENV, str(cert))
    monkeypatch.setenv(KEY_ENV, str(key))

    assert build_ssl_options() == {'certfile': str(cert), 'keyfile': str(key)}


def test_ssl_options_empty_env_uses_default(tmp_path, monkeypatch):
    cert, key = _pair(tmp_path)
    monkeypatch.setattr('util.https_cert.DEFAULT_CERT_FILE', str(cert))
    monkeypatch.setattr('util.https_cert.DEFAULT_KEY_FILE', str(key))
    monkeypatch.setenv(CERT_ENV, '')
    monkeypatch.setenv(KEY_ENV, '')

    assert build_ssl_options() == {'certfile': str(cert), 'keyfile': str(key)}


def test_ssl_options_unset_env_uses_default(tmp_path, monkeypatch):
    cert, key = _pair(tmp_path)
    monkeypatch.setattr('util.https_cert.DEFAULT_CERT_FILE', str(cert))
    monkeypatch.setattr('util.https_cert.DEFAULT_KEY_FILE', str(key))
    monkeypatch.delenv(CERT_ENV, raising=False)
    monkeypatch.delenv(KEY_ENV, raising=False)

    assert build_ssl_options() == {'certfile': str(cert), 'keyfile': str(key)}


def test_ssl_options_ignores_openssl_ssl_cert_file(tmp_path, monkeypatch):
    cert, key = _pair(tmp_path)
    monkeypatch.setattr('util.https_cert.DEFAULT_CERT_FILE', str(cert))
    monkeypatch.setattr('util.https_cert.DEFAULT_KEY_FILE', str(key))
    monkeypatch.delenv(CERT_ENV, raising=False)
    monkeypatch.delenv(KEY_ENV, raising=False)
    monkeypatch.setenv('SSL_CERT_FILE', str(tmp_path / 'not-used-as-server-cert.pem'))
    monkeypatch.setenv('SSL_KEY_FILE', str(tmp_path / 'not-used-as-server-key.key'))

    assert build_ssl_options() == {'certfile': str(cert), 'keyfile': str(key)}


def test_ssl_options_missing_cert(tmp_path, monkeypatch):
    _, key = _pair(tmp_path)
    missing = tmp_path / 'missing.pem'
    monkeypatch.setenv(CERT_ENV, str(missing))
    monkeypatch.setenv(KEY_ENV, str(key))

    with pytest.raises(FileNotFoundError, match='missing.pem'):
        build_ssl_options()


def test_ssl_options_missing_key(tmp_path, monkeypatch):
    cert, key = _pair(tmp_path)
    os.remove(key)
    monkeypatch.setenv(CERT_ENV, str(cert))
    monkeypatch.setenv(KEY_ENV, str(key))

    with pytest.raises(FileNotFoundError, match='service.key'):
        build_ssl_options()


def test_ssl_options_rejects_empty_file(tmp_path, monkeypatch):
    cert, key = _pair(tmp_path)
    cert.write_text('')
    monkeypatch.setenv(CERT_ENV, str(cert))
    monkeypatch.setenv(KEY_ENV, str(key))

    with pytest.raises(FileNotFoundError, match='service.pem'):
        build_ssl_options()


def test_ssl_options_rejects_directory(tmp_path, monkeypatch):
    _, key = _pair(tmp_path)
    cert_dir = tmp_path / 'mounted-as-dir'
    cert_dir.mkdir()
    monkeypatch.setenv(CERT_ENV, str(cert_dir))
    monkeypatch.setenv(KEY_ENV, str(key))

    with pytest.raises(FileNotFoundError, match='mounted-as-dir'):
        build_ssl_options()
