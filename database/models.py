from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

__all__ = ["Base", "User", "Group", "Order"]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]]
    language: Mapped[Optional[str]]

    def orders_amount(self, session: Session) -> int:
        with session:
            stmt = select(Order).where(Order.user_id == self.id)
            return len(session.scalars(stmt).all())

    def orders_sum(self, session: Session) -> int:
        with session:
            stmt = select(Order.group_id).where(Order.user_id == self.id)

            orders_total = 0
            for group_id in session.scalars(stmt).all():
                stmt = select(Group.price).where(Group.id == group_id)
                orders_total += session.scalar(stmt)

            return orders_total

    def __repr__(self) -> str:
        return (
            f"User(id = {self.id}, "
            f"name = {self.name}, "
            f"language = {self.language})"
        )


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[float]
    name: Mapped[Optional[str]]
    tag: Mapped[Optional[str]]
    url: Mapped[str]
    founded: Mapped[datetime]


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    group_id: Mapped[int]