#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func

from model import BaseModel


class MovieInfoModel(BaseModel):
    """电影信息"""
    __tablename__ = 'movie_info'

    id = Column(Integer, primary_key=True)  # 自增
    title_translation = Column(String(255), default='', nullable=False, comment='译名')
    title_original = Column(String(255), default='', nullable=False, comment='片名')
    year = Column(String(50), default='', nullable=False, comment='年代')
    country = Column(String(255), default='', nullable=False, comment='产地')
    genre = Column(String(50), default='', nullable=False, comment='类别')
    language = Column(String(50), default='', nullable=False, comment='语言')
    release_date = Column(String(50), default='', nullable=False, comment='上映日期')
    douban_rating = Column(String(50), default='', nullable=False, comment='豆瓣评分')
    imdb_rating = Column(String(50), default='', nullable=False, comment='IMDb评分')
    file_format = Column(String(50), default='', nullable=False, comment='文件格式')
    file_size = Column(String(50), default='', nullable=False, comment='文件大小')
    duration = Column(String(50), default='', nullable=False, comment='片长')
    director = Column(String(255), default='', nullable=False, comment='导演')
    cast = Column(Text, default='', nullable=False, comment='主演')
    synopsis = Column(Text, default='', nullable=False, comment='简介')
    subtitle_type = Column(String(50), default='', nullable=False, comment='字幕类型')
    video_size = Column(String(50), default='', nullable=False, comment='视频尺寸')
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now(), comment='最新更新时间')  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now(), comment='创建时间')  # 创建时间

    @classmethod
    def create_movie(cls, session, **kwargs):
        """插入新电影信息"""
        new_movie = cls(**kwargs)
        session.add(new_movie)
        session.commit()
        return new_movie

    @classmethod
    def get_movie_by_id(cls, session, movie_id):
        """根据电影ID查询电影信息"""
        return session.query(cls).filter_by(id=movie_id).first()

    @classmethod
    def get_all_movies(cls, session):
        """查询所有电影信息"""
        return session.query(cls).all()

    @classmethod
    def update_movie(cls, session, movie_id, **kwargs):
        """根据电影ID更新电影信息"""
        movie = cls.get_movie_by_id(session, movie_id)
        if movie:
            for key, value in kwargs.items():
                setattr(movie, key, value)
            session.commit()
        return movie

    @classmethod
    def delete_movie(cls, session, movie_id):
        """根据电影ID删除电影信息"""
        movie = cls.get_movie_by_id(session, movie_id)
        if movie:
            session.delete(movie)
            session.commit()
        return movie
