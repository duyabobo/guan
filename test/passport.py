#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker

from model.passport import PassportModel
from database import engine


def get_db_session():
    return sessionmaker(bind=engine)()


if __name__ == '__main__':
    dbSession = get_db_session()
    p = PassportModel.getByOpenid(dbSession, "openid")
    # print p.id
    p = PassportModel.addByOpenid(dbSession, "openid")
    print p.id
    p = PassportModel.getByOpenid(dbSession, "openid")
    print p.id
