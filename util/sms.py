#!/usr/bin/env python
# coding=utf-8  # todo 需要营业执照，所以短信验证码先不支持的

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.auth.credentials import StsTokenCredential
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest

credentials = AccessKeyCredential('<your-access-key-id>', '<your-access-key-secret>')
# use STS Token
# credentials = StsTokenCredential('<your-access-key-id>', '<your-access-key-secret>', '<your-sts-token>')
client = AcsClient(region_id='cn-beijing', credential=credentials)

request = SendSmsRequest()
request.set_accept_format('json')

response = client.do_action_with_exception(request)
print(response)
