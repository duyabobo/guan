#! /usr/bin/env python
# -*- coding: utf-8 -*-

import taskingai

from model.movie.movie_info import MovieInfoModel

taskingai.init(api_key='tkezLyJcr5orpdhZWM3k0qgRWtnBt9NX', host='http://localhost:8080')


def push_a_record(title, content):
    """上传数据到tasking的records"""
    record = taskingai.retrieval.create_record(
        collection_id="DbgYz0dxify6yzteyhqflbv2",
        type="text",
        title=title,
        content=content,
        text_splitter={"type": "token", "chunk_size": 200, "chunk_overlap": 20},
        # metadata= {"file_name":"machine_learning.pdf"}
    )
    return record


if __name__ == "__main__":
    movies = MovieInfoModel.get_all_movies()
    for movie in movies:
        """
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
    u'◎导　　演': 'director',
    u'◎主　　演': 'cast',
    u'◎简　　介': 'synopsis',"""
        content = f"译名：{movie.title_translation}\n" \
                  f"片名：{movie.title_original}\n"  \
                  f"导演：{movie.director}\n" \
                  f"主演：{movie.cast}\n" \
                  f"简介：{movie.synopsis}\n" \
                  f"年代：{movie.year}\n" \
                  f"产地：{movie.country}\n" \
                  f"类别：{movie.genre}\n" \
                  f"语言：{movie.language}\n" \
                  f"上映日期：{movie.release_date}\n" \
                  f"豆瓣评分：{movie.douban_rating}\n" \
                  f"IMDb评分：{movie.imdb_rating}\n" \
                  f"文件格式：{movie.file_format}\n" \
                  f"片长：{movie.duration}\n" \
                  f"字幕类型：{movie.subtitle_type}\n" \
                  f"视频尺寸：{movie.video_size}\n"
        record = push_a_record(movie.title_original, content)
        print(record)
