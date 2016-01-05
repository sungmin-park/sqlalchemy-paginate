from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_paginate import Pagination

engine = create_engine('sqlite://')
Session = sessionmaker(bind=engine)
Base = declarative_base(bind=engine)


class Item(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)

    __tablename__ = 'item'


Base.metadata.create_all()


@contextmanager
def ctx(count, page=1):
    def first(item):
        return item[0]

    session = Session()
    map(session.add, [Item() for _ in range(count)])
    try:
        session.flush()
        pagination = Pagination(session.query(Item.id), page=page, per_page=3,
                                per_nav=3, map_=first)
        assert pagination.total == count
        yield pagination
    finally:
        session.rollback()
        session.close()


def test_normalize_page():
    with ctx(0) as pagination:
        assert pagination.page == 1

    # prevent overflow
    with ctx(0, 2) as pagination:
        assert pagination.page == 1

    # prevent underflow
    with ctx(0, 0) as pagination:
        assert pagination.page == 1


def test_last_page():
    with ctx(0) as p:
        assert p.last == 1
    with ctx(1) as p:
        assert p.last == 1
    with ctx(2) as p:
        assert p.last == 1
    with ctx(3) as p:
        assert p.last == 1

    with ctx(4) as p:
        assert p.last == 2
    with ctx(5) as p:
        assert p.last == 2
    with ctx(6) as p:
        assert p.last == 2


def test_nav_head():
    with ctx(0) as p:
        assert p.nav_head == 1

    with ctx(31, 1) as p:
        assert p.nav_head == 1
    with ctx(31, 2) as p:
        assert p.nav_head == 1
    with ctx(31, 3) as p:
        assert p.nav_head == 1

    with ctx(31, 4) as p:
        assert p.nav_head == 4
    with ctx(31, 5) as p:
        assert p.nav_head == 4
    with ctx(31, 6) as p:
        assert p.nav_head == 4

    with ctx(31, 7) as p:
        assert p.nav_head == 7
    with ctx(31, 8) as p:
        assert p.nav_head == 7
    with ctx(31, 9) as p:
        assert p.nav_head == 7


def test_nav_tail():
    with ctx(0) as p:
        assert p.nav_tail == 1

    with ctx(31, 1) as p:
        assert p.nav_tail == 3
    with ctx(31, 2) as p:
        assert p.nav_tail == 3
    with ctx(31, 3) as p:
        assert p.nav_tail == 3

    with ctx(31, 4) as p:
        assert p.nav_tail == 6
    with ctx(31, 5) as p:
        assert p.nav_tail == 6
    with ctx(31, 6) as p:
        assert p.nav_tail == 6

    with ctx(31, 7) as p:
        assert p.nav_tail == 9
    with ctx(31, 8) as p:
        assert p.nav_tail == 9
    with ctx(31, 9) as p:
        assert p.nav_tail == 9

    with ctx(31, 10) as p:
        assert p.nav_tail == 11
    with ctx(31, 11) as p:
        assert p.nav_tail == 11
    with ctx(31, 12) as p:
        assert p.page == 11
        assert p.nav_tail == 11


def test_pages():
    with ctx(0) as p:
        assert p.pages == [1]

    with ctx(31, 1) as p:
        assert p.pages == [1, 2, 3]
    with ctx(31, 2) as p:
        assert p.pages == [1, 2, 3]
    with ctx(31, 3) as p:
        assert p.pages == [1, 2, 3]

    with ctx(31, 4) as p:
        assert p.pages == [4, 5, 6]
    with ctx(31, 5) as p:
        assert p.pages == [4, 5, 6]
    with ctx(31, 6) as p:
        assert p.pages == [4, 5, 6]

    with ctx(31, 7) as p:
        assert p.pages == [7, 8, 9]
    with ctx(31, 8) as p:
        assert p.pages == [7, 8, 9]
    with ctx(31, 9) as p:
        assert p.pages == [7, 8, 9]

    with ctx(31, 10) as p:
        assert p.pages == [10, 11]
    with ctx(31, 11) as p:
        assert p.pages == [10, 11]
    with ctx(31, 12) as p:
        assert p.pages == [10, 11]


def test_items():
    with ctx(0) as p:
        assert p.items == []

    with ctx(31, 1) as p:
        assert p.items == [1, 2, 3]
    with ctx(31, 2) as p:
        assert p.items == [4, 5, 6]
    with ctx(31, 3) as p:
        assert p.items == [7, 8, 9]

    with ctx(31, 10) as p:
        assert p.items == [28, 29, 30]
    with ctx(31, 11) as p:
        assert p.items == [31]
    with ctx(31, 12) as p:
        assert p.items == [31]
