#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os

import pytest

from util.https_cert import build_ssl_options


def _pair(directory):
    cert = directory / 'service.pem'
    key = directory / 'service.key'
    cert.write_text('cert')
    key.write_text('key')
    return cert, key


def test_ssl_options_reads_env_paths(tmp_path, monkeypatch):
    cert, key = _pair(tmp_path)
    monkeypatch.setenv('SSL_CERT_FILE', str(cert))
    monkeypatch.setenv('SSL_KEY_FILE', str(key))

    assert build_ssl_options() == {'certfile': str(cert), 'keyfile': str(key)}


def test_ssl_options_empty_env_uses_default(tmp_path, monkeypatch):
    cert, key = _pair(tmp_path)
    monkeypatch.setattr('util.https_cert.DEFAULT_CERT_FILE', str(cert))
    monkeypatch.setattr('util.https_cert.DEFAULT_KEY_FILE', str(key))
    monkeypatch.setenv('SSL_CERT_FILE', '')
    monkeypatch.setenv('SSL_KEY_FILE', '')

    assert build_ssl_options() == {'certfile': str(cert), 'keyfile': str(key)}


def test_ssl_options_unset_env_uses_default(tmp_path, monkeypatch):
    cert, key = _pair(tmp_path)
    monkeypatch.setattr('util.https_cert.DEFAULT_CERT_FILE', str(cert))
    monkeypatch.setattr('util.https_cert.DEFAULT_KEY_FILE', str(key))
    monkeypatch.delenv('SSL_CERT_FILE', raising=False)
    monkeypatch.delenv('SSL_KEY_FILE', raising=False)

    assert build_ssl_options() == {'certfile': str(cert), 'keyfile': str(key)}


def test_ssl_options_missing_cert(tmp_path, monkeypatch):
    _, key = _pair(tmp_path)
    missing = tmp_path / 'missing.pem'
    monkeypatch.setenv('SSL_CERT_FILE', str(missing))
    monkeypatch.setenv('SSL_KEY_FILE', str(key))

    with pytest.raises(FileNotFoundError, match='missing.pem'):
        build_ssl_options()


def test_ssl_options_missing_key(tmp_path, monkeypatch):
    cert, key = _pair(tmp_path)
    os.remove(key)
    monkeypatch.setenv('SSL_CERT_FILE', str(cert))
    monkeypatch.setenv('SSL_KEY_FILE', str(key))

    with pytest.raises(FileNotFoundError, match='service.key'):
        build_ssl_options()


def test_ssl_options_rejects_empty_file(tmp_path, monkeypatch):
    cert, key = _pair(tmp_path)
    cert.write_text('')
    monkeypatch.setenv('SSL_CERT_FILE', str(cert))
    monkeypatch.setenv('SSL_KEY_FILE', str(key))

    with pytest.raises(FileNotFoundError, match='service.pem'):
        build_ssl_options()


def test_ssl_options_rejects_directory(tmp_path, monkeypatch):
    _, key = _pair(tmp_path)
    cert_dir = tmp_path / 'mounted-as-dir'
    cert_dir.mkdir()
    monkeypatch.setenv('SSL_CERT_FILE', str(cert_dir))
    monkeypatch.setenv('SSL_KEY_FILE', str(key))

    with pytest.raises(FileNotFoundError, match='mounted-as-dir'):
        build_ssl_options()
