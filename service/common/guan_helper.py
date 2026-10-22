#! /usr/bin/env python
# -*- coding: utf-8 -*-


class GuanHelper(object):

    @classmethod
    def getActivityImg(cls, address, thumbnails):
        if not address:
            return ''
        if thumbnails:
            return address.thumbnails_img
        return address.img
