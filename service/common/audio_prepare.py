#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""按文件魔数识别音频格式，只把方舟原生支持的格式直接送出。

微信真机 mp3/aac/wav 与方舟纯音频格式重叠，无需转码。
开发者工具 / 桌面微信常忽略 format，固定产出 WebM/Opus；方舟不收，这里直接拒绝。
"""
import logging

logger = logging.getLogger(__name__)

FORMAT_MP3 = 'mp3'
FORMAT_WAV = 'wav'
FORMAT_AAC = 'aac'
FORMAT_M4A = 'm4a'
FORMAT_WEBM = 'webm'

ARK_NATIVE_FORMATS = frozenset({FORMAT_MP3, FORMAT_WAV, FORMAT_AAC, FORMAT_M4A})

MIME_BY_FORMAT = {
    FORMAT_MP3: 'audio/mpeg',
    FORMAT_WAV: 'audio/wav',
    FORMAT_AAC: 'audio/aac',
    FORMAT_M4A: 'audio/mp4',
    FORMAT_WEBM: 'audio/webm',
}
FALLBACK_MIME = 'application/octet-stream'

_MIN_HEADER_BYTES = 12
_WEBM_MAGIC = b'\x1a\x45\xdf\xa3'
_RIFF_MAGIC = b'RIFF'
_WAVE_MAGIC = b'WAVE'
_ID3_MAGIC = b'ID3'
_FTYP_MAGIC = b'ftyp'
# MPEG 帧同步：11 个 1；AAC ADTS 同步：12 个 1。
_MPEG_SYNC_MASK = 0xe0
_MPEG_SYNC_BITS = 0xe0
_AAC_ADTS_MASK = 0xf6
_AAC_ADTS_BITS = 0xf0


def detect_audio_format(audio_bytes):
    data = audio_bytes or b''
    if len(data) < _MIN_HEADER_BYTES:
        return ''
    if data[:4] == _WEBM_MAGIC:
        return FORMAT_WEBM
    if data[:4] == _RIFF_MAGIC and data[8:12] == _WAVE_MAGIC:
        return FORMAT_WAV
    if data[:3] == _ID3_MAGIC:
        return FORMAT_MP3
    if data[4:8] == _FTYP_MAGIC:
        return FORMAT_M4A
    if data[0] == 0xff and (data[1] & _MPEG_SYNC_MASK) == _MPEG_SYNC_BITS:
        if (data[1] & _AAC_ADTS_MASK) == _AAC_ADTS_BITS:
            return FORMAT_AAC
        return FORMAT_MP3
    return ''


def content_type_for(audio_bytes):
    fmt = detect_audio_format(audio_bytes)
    return MIME_BY_FORMAT.get(fmt, FALLBACK_MIME)


def prepare_ark_audio(audio_bytes):
    """返回 (bytes, ark_format)。无法直传时返回 (None, '')。"""
    fmt = detect_audio_format(audio_bytes)
    if fmt in ARK_NATIVE_FORMATS:
        logger.info("语音可直接提交方舟 format=%s bytes=%s", fmt, len(audio_bytes))
        return audio_bytes, fmt
    if fmt == FORMAT_WEBM:
        logger.warning(
            "收到 WebM/Opus（多为开发者工具），方舟不支持，请用手机真机录音 bytes=%s",
            len(audio_bytes),
        )
        return None, ''
    logger.warning("不支持的音频格式 format=%s bytes=%s", fmt or 'unknown', len(audio_bytes or b''))
    return None, ''
