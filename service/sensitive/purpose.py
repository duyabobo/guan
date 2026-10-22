#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.const.identity import PURPOSE_MIN_LENGTH


def purpose_accepted(purpose):
    text = (purpose or '').strip()
    return len(text) >= PURPOSE_MIN_LENGTH
