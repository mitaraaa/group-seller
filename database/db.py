import os
import logging

from aiogram import types
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from api.steam import GroupInfo

from .models import Base, Group, User

sqlite_file_path = os.getenv("DATABASE_PATH")
engine = create_engine(f"sqlite:///{sqlite_file_path}")

Base.metadata.create_all(bind=engine)
session = Session(engine)


def create_group(info: GroupInfo, price: int):
    with session:
        try:
            group = Group(**(dict(vars(info).items())), price=price)
            session.add(group)
            session.commit()
        except IntegrityError:
            logging.warn("Tried adding group that already exists")


def get_group_by_id(id: int) -> Group | None:
    with session:
        stmt = select(Group).where(Group.id == id)
        return session.scalar(stmt)


def get_group_by_url(url: str) -> Group | None:
    with session:
        stmt = select(Group).where(Group.url == url)
        return session.scalar(stmt)


def create_user(user: types.User):
    with session:
        user = User(id=user.id, name=user.first_name or user.username)
        session.add(user)
        session.commit()


def get_user(user_id: int) -> User | None:
    with session:
        stmt = select(User).where(User.id == user_id)
        return session.scalar(stmt)
