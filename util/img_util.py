# -*- coding:utf-8 -*-
import cv2
import numpy as np


def dodgeV2(image, mask):
    return cv2.divide(image, 255 - mask, scale=256)


def rgb_to_sketch(buffer_data):
    # 手绘风处理，输入一个图片二进制流，输出手绘风图片二进制流
    img_np_arr = np.frombuffer(buffer_data, np.uint8)
    img_rgb = cv2.imdecode(img_np_arr, cv2.IMREAD_COLOR)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    img_gray_inv = 255 - img_gray
    img_blur = cv2.GaussianBlur(img_gray_inv, ksize=(21, 21), sigmaX=0, sigmaY=0)
    img_blend = dodgeV2(img_gray, img_blur)
    return cv2.imencode(".jpg", img_blend)[1].tobytes()
