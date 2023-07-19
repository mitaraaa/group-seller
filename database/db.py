import os
import logging

from aiogram import types
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from api.steam import GroupInfo

from .models import Base, Group, Order, User

sqlite_file_path = os.getenv("DATABASE_PATH")
engine = create_engine(f"sqlite:///{sqlite_file_path}")

Base.metadata.create_all(bind=engine)
session = Session(engine)


def create_group(info: GroupInfo, price: float | str):
    with session:
        try:
            group = Group(**(dict(vars(info).items())), price=float(price))
            session.add(group)
            session.commit()
        except IntegrityError:
            logging.warn("Tried adding group that already exists")


def get_group_by_id(id: int) -> Group | None:
    with session:
        stmt = select(Group).where(Group.id == id)
        return session.scalar(stmt)


def get_user_by_username(username: str):
    with session:
        stmt = select(User).where(User.username == username)
        return session.scalar(stmt)


def get_group_by_url(url: str) -> Group | None:
    with session:
        stmt = select(Group).where(Group.url == url)
        return session.scalar(stmt)


def get_all_groups():
    with session:
        stmt = select(Group).where(Group.sold == False)
        return session.scalars(stmt).all()


def set_sold(group_id: int):
    group = get_group_by_id(group_id)

    if not group:
        return

    with session:
        group.sold = True
        session.add(group)
        session.commit()


def create_user(user: types.User):
    with session:
        try:
            user = User(id=user.id, username=user.username)
            session.add(user)
            session.commit()
        except IntegrityError:
            logging.warn("Tried adding user that already exists")


def get_user(user_id: int) -> User | None:
    with session:
        stmt = select(User).where(User.id == user_id)
        return session.scalar(stmt)


def create_order(
    user_id: int, group_id: int, method: str, price: float
) -> None:
    with session:
        order = Order(
            user_id=user_id, group_id=group_id, method=method, price=price
        )
        session.add(order)
        session.flush()
        order_id = order.id
        session.commit()
        return order_id


def get_order(order_id: int) -> Order | None:
    with session:
        stmt = select(Order).where(Order.id == order_id)
        return session.scalar(stmt)


def get_user_orders(user_id: int) -> list[Order]:
    with session:
        stmt = select(Order).where(Order.user_id == user_id)
        return session.scalars(stmt).all()


def remove_order(order_id: int):
    with session:
        stmt = select(Order).where(Order.id == order_id)
        order = session.scalar(stmt)
        session.flush()
        session.delete(order)
        session.commit()
