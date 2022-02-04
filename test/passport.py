#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker

from model.passport import Passport
from database import engine


def get_db_session():
    return sessionmaker(bind=engine)()


if __name__ == '__main__':
    db_session = get_db_session()
    p = Passport.get_by_openid(db_session, "openid")
    # print p.id
    p = Passport.add_by_openid(db_session, "openid")
    print p.id
    p = Passport.get_by_openid(db_session, "openid")
    print p.id
