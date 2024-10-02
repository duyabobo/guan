#!/usr/bin/env python
# coding=utf-8

import smtplib  # smtp服务器
from email.mime.text import MIMEText  # 邮件文本

# 邮件构建

subject = "邮件认证"  # 邮件标题
sender = "13366397755@163.com"  # 发送方
password = "SVKSYFUAAQEKHCLP"  # 邮箱密码


def send_email_verify(receiver, code):
    smtp = smtplib.SMTP_SSL("smtp.163.com", 994)  # 实例化smtp服务器
    smtp.login(sender, password)  # 发件人登录

    content = "您正在《关关雎鸠》小程序进行工作认证，本次验证码是:%s，5分钟有效。\n如果不是本人请求，请忽略。" % code
    message = MIMEText(content, "plain", "utf-8")
    message['Subject'] = subject  # 邮件标题
    message['To'] = receiver  # 收件人
    message['From'] = sender  # 发件人

    smtp.sendmail(sender, [receiver], message.as_string())  # as_string 对 message 的消息进行了封装


if __name__ == '__main__':
    send_email_verify("809618694@qq.com", "1234")
