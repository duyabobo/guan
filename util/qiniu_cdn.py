#! /usr/bin/env python
# -*- coding: utf-8 -*-
import util.config
from qiniu import Auth, put_data


class Qiniu():
    def __init__(self):
        self.access_key = util.config.get("qiniu", "access_key")
        self.secret_key = util.config.get("qiniu", "secret_key")
        # 要上传的空间
        self.bucket_name = util.config.get("qiniu", "head_img_bucket_name")
        # 构建鉴权对象
        self.auth = Auth(self.access_key, self.secret_key)

    def get_token(self, key):
        """

        :param key: 文件名
        :return: 上传令牌
        """
        policy = {
            'scope': self.bucket_name,
            'mimeLimit': 'image/jpeg;image/png',
            'deadline': 3600
        }
        # 3600为token过期时间，秒为单位。3600等于一小时
        token = self.auth.upload_token(self.bucket_name, key, 3600, policy)
        return token

    def upload_stream(self, filename, stream_data):
        """

        :param filename: 文件名
        :param stream_data: 二进制数据
        :return: 无
        """
        # 上传后保存的文件名
        key = filename
        # 生成上传 Token，可以指定过期时间等
        token = self.auth.upload_token(self.bucket_name, key, 3600)
        # 要上传文件的本地路径
        # localfile = file_path
        ret, info = put_data(up_token=token, key=key, data=stream_data)
        assert ret and ret['key'] == key
        # assert ret['hash'] == etag_stream(stream_data)
