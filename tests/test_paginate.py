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


def paginate(count, page=1):
    def first(item):
        return item[0]

    session = Session()
    map(session.add, [Item() for _ in range(count)])
    try:
        session.flush()
        pagination = Pagination(session.query(Item.id), page=page, per_page=3,
                                per_nav=3, map_=first)
        assert pagination.total == count
        return pagination
    finally:
        session.rollback()
        session.close()


def test_normalize_page():
    assert paginate(0).page == 1

    # prevent overflow
    assert paginate(0, 2).page == 1

    # prevent underflow
    assert paginate(0, 0).page == 1


def test_last_page():
    assert paginate(0).last == 1

    assert paginate(1).last == 1
    assert paginate(2).last == 1
    assert paginate(3).last == 1

    assert paginate(4).last == 2
    assert paginate(5).last == 2
    assert paginate(6).last == 2


def test_nav_head():
    assert paginate(0).nav_head == 1

    assert paginate(31, 1).nav_head == 1
    assert paginate(31, 2).nav_head == 1
    assert paginate(31, 3).nav_head == 1

    assert paginate(31, 4).nav_head == 4
    assert paginate(31, 5).nav_head == 4
    assert paginate(31, 6).nav_head == 4

    assert paginate(31, 7).nav_head == 7
    assert paginate(31, 8).nav_head == 7
    assert paginate(31, 9).nav_head == 7


def test_nav_tail():
    assert paginate(0).nav_tail == 1

    assert paginate(31, 1).nav_tail == 3
    assert paginate(31, 2).nav_tail == 3
    assert paginate(31, 3).nav_tail == 3

    assert paginate(31, 4).nav_tail == 6
    assert paginate(31, 5).nav_tail == 6
    assert paginate(31, 6).nav_tail == 6

    assert paginate(31, 7).nav_tail == 9
    assert paginate(31, 8).nav_tail == 9
    assert paginate(31, 9).nav_tail == 9

    assert paginate(31, 10).nav_tail == 11
    assert paginate(31, 11).nav_tail == 11
    p = paginate(31, 12)
    assert p.page == 11
    assert p.nav_tail == 11


def test_pages():
    assert paginate(0).pages == [1]

    assert paginate(31, 1).pages == [1, 2, 3]
    assert paginate(31, 2).pages == [1, 2, 3]
    assert paginate(31, 3).pages == [1, 2, 3]

    assert paginate(31, 4).pages == [4, 5, 6]
    assert paginate(31, 5).pages == [4, 5, 6]
    assert paginate(31, 6).pages == [4, 5, 6]

    assert paginate(31, 7).pages == [7, 8, 9]
    assert paginate(31, 8).pages == [7, 8, 9]
    assert paginate(31, 9).pages == [7, 8, 9]

    assert paginate(31, 10).pages == [10, 11]
    assert paginate(31, 11).pages == [10, 11]
    assert paginate(31, 12).pages == [10, 11]


def test_items():
    assert paginate(0).items == []

    assert paginate(31, 1).items == [1, 2, 3]
    assert paginate(31, 2).items == [4, 5, 6]
    assert paginate(31, 3).items == [7, 8, 9]

    assert paginate(31, 10).items == [28, 29, 30]
    assert paginate(31, 11).items == [31]
    assert paginate(31, 12).items == [31]


def test_first():
    assert paginate(0).first == 1
