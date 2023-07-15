import os

from aiogram import types
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from .models import Base, User

sqlite_file_path = os.getenv("DATABASE_PATH")
engine = create_engine(f"sqlite:///{sqlite_file_path}")

Base.metadata.create_all(bind=engine)
session = Session(engine)


def create_user(user: types.User) -> None:
    with session:
        user = User(id=user.id, name=user.first_name or user.username)
        session.add(user)
        session.commit()


def get_user(user_id: int) -> User | None:
    with session:
        stmt = select(User).where(User.id == user_id)
        return session.scalar(stmt)
