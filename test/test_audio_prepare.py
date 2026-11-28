#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from service.common.audio_prepare import (
    FORMAT_AAC,
    FORMAT_M4A,
    FORMAT_MP3,
    FORMAT_WAV,
    FORMAT_WEBM,
    content_type_for,
    detect_audio_format,
    prepare_ark_audio,
)


def test_detect_webm_mp3_wav_aac_m4a():
    assert detect_audio_format(b'\x1a\x45\xdf\xa3' + b'\x00' * 12) == FORMAT_WEBM
    assert detect_audio_format(b'ID3' + b'\x00' * 12) == FORMAT_MP3
    assert detect_audio_format(b'\xff\xfb' + b'\x00' * 12) == FORMAT_MP3
    assert detect_audio_format(b'\xff\xf1' + b'\x00' * 12) == FORMAT_AAC
    assert detect_audio_format(b'xxxxftyp' + b'\x00' * 4) == FORMAT_M4A
    assert detect_audio_format(b'RIFF\x00\x00\x00\x00WAVE' + b'\x00' * 4) == FORMAT_WAV
    assert detect_audio_format(b'') == ''


def test_content_type_follows_magic():
    assert content_type_for(b'\x1a\x45\xdf\xa3' + b'\x00' * 12) == 'audio/webm'
    assert content_type_for(b'ID3' + b'\x00' * 12) == 'audio/mpeg'
    assert content_type_for(b'not-audio') == 'application/octet-stream'


def test_prepare_native_passthrough():
    mp3 = b'ID3' + b'\x00' * 32
    prepared, fmt = prepare_ark_audio(mp3)
    assert fmt == FORMAT_MP3
    assert prepared is mp3
    wav = b'RIFF\x00\x00\x00\x00WAVE' + b'\x00' * 16
    prepared, fmt = prepare_ark_audio(wav)
    assert fmt == FORMAT_WAV
    assert prepared is wav


def test_prepare_unknown_rejects():
    prepared, fmt = prepare_ark_audio(b'not-an-audio')
    assert prepared is None
    assert fmt == ''


def test_prepare_webm_rejects_without_transcode():
    prepared, fmt = prepare_ark_audio(b'\x1a\x45\xdf\xa3' + b'\x00' * 32)
    assert prepared is None
    assert fmt == ''
