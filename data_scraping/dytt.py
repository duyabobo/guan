#!/usr/bin/env python
# coding=utf-8
import requests
import chardet
from bs4 import BeautifulSoup
import sys
import codecs

# 设置标准输出编码为 UTF-8
reload(sys)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

# 目标URL
url = 'http://www.dytt89.com/i/112423.html'

# 定义键
one_line_key = {
    u'◎译　　名': 1,
    u'◎片　　名': 1,
    u'◎年　　代': 1,
    u'◎产　　地': 1,
    u'◎类　　别': 1,
    u'◎语　　言': 1,
    u'◎上映日期': 1,
    u'◎豆瓣评分': 1,
    u'◎IMDb评分': 1,
    u'◎文件格式': 1,
    u'◎文件大小': 1,
    u'◎片　　长': 1,
}

multi_line_key = {
    u'◎导　　演': 1,
    u'◎主　　演': 1,
    u'◎简　　介': 1,
    u'◎影片截图': 1,
}

if __name__ == '__main__':
    # 发送HTTP GET请求
    response = requests.get(url)

    # 使用chardet检测网页编码
    detected_encoding = chardet.detect(response.content)['encoding']
    # print(u'检测到的编码:', detected_encoding)

    # 根据检测结果设置编码
    response.encoding = detected_encoding

    # 检查请求是否成功
    if response.status_code == 200:
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找包含信息的 div
        info_div = soup.find('div', id='Zoom')

        # 提取信息
        if info_div:
            # 定义一个字典来存储信息
            movie_info = {}
            current_key = None

            # 提取每一个信息项
            for line in info_div.stripped_strings:
                pre_len = 0
                for k in one_line_key.keys():
                    if line.startswith(k):
                        current_key = k[1:]
                        pre_len = len(k)
                        break
                for k in multi_line_key.keys():
                    if line.startswith(k):
                        current_key = k[1:]
                        pre_len = len(k)
                        break

                if current_key:
                    value = line[pre_len:].strip()
                    if current_key in one_line_key:
                        movie_info[current_key] = value
                    else:
                        if current_key not in movie_info:
                            movie_info[current_key] = []
                        movie_info[current_key].append(value)

            # 打印解析结果
            for key, value in movie_info.items():
                if isinstance(value, list):
                    value = '\n'.join(value)
                print(u'{}: {}'.format(key, value))  # 使用 Unicode 输出


        else:
            print(u'没有找到包含信息的 div')

    else:
        print(u'请求失败，状态码:', response.status_code)
