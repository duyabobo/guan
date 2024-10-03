#!/usr/bin/env python
# coding=utf-8
import codecs
import sys

import chardet
import requests
from bs4 import BeautifulSoup

from model.movie.movie_info import MovieInfoModel

# 设置标准输出编码为 UTF-8
reload(sys)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

# 定义键
# 一行数据的键与 movie_info 列的对应关系
one_line_mapping = {
    u'◎译　　名': 'title_translation',
    u'◎片　　名': 'title_original',
    u'◎年　　代': 'year',
    u'◎产　　地': 'country',
    u'◎类　　别': 'genre',
    u'◎语　　言': 'language',
    u'◎上映日期': 'release_date',
    u'◎豆瓣评分': 'douban_rating',
    u'◎IMDb评分': 'imdb_rating',
    u'◎文件格式': 'file_format',
    u'◎文件大小': 'file_size',
    u'◎片　　长': 'duration',
    u'◎字　　幕': 'subtitle_type',
    u'◎视频尺寸': 'video_size',
}

# 多行数据的键与 movie_info 列的对应关系
multi_line_mapping = {
    u'◎导　　演': 'director',
    u'◎主　　演': 'cast',
    u'◎简　　介': 'synopsis',
    # u'◎影片截图': 'screenshot',  # 如果有需要，添加一个截图字段
}


def get_one_movie(movie_id):
    url = 'http://www.dytt89.com/i/%d.html' % movie_id
    response = requests.get(url)

    # 使用chardet检测网页编码
    detected_encoding = "GB2312" # chardet.detect(response.content)['encoding']
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
                for k in one_line_mapping.keys():
                    if line.startswith(k):
                        current_key = one_line_mapping[k]
                        pre_len = len(k)
                        break
                for k in multi_line_mapping.keys():
                    if line.startswith(k):
                        current_key = multi_line_mapping[k]
                        pre_len = len(k)
                        break

                value = line[pre_len:].strip()
                if value.startswith(u'【下载地址】'):
                    break
                if current_key:
                    if current_key in one_line_mapping:
                        movie_info[current_key] = value
                    elif not value.startswith(u'◎'):
                        if current_key not in movie_info:
                            movie_info[current_key] = []
                        movie_info[current_key].append(value)

            # 打印解析结果
            _movie_info = {'id': movie_id, 'head_img': info_div.find('img')['src'], 'create_time': soup.find('span', class_='updatetime').text[5:]}
            for key, value in movie_info.items():
                if isinstance(value, list):
                    value = '\n'.join(value).strip("\n")
                _movie_info[key] = value
                print(u'{}: {}'.format(key, value))  # 使用 Unicode 输出

            # 保存到数据库
            if MovieInfoModel.get_movie_by_id(movie_id):
                MovieInfoModel.update_movie(movie_id, **_movie_info)
            else:
                MovieInfoModel.create_movie(**_movie_info)
        else:
            print(u'没有找到包含信息的 div')

    else:
        print(u'请求失败，状态码:', response.status_code)


if __name__ == '__main__':
    # 发送HTTP GET请求
    for i in range(100000, 120000):
        try:
            get_one_movie(i)
        except Exception as e:
            print('err: %s' % e)
