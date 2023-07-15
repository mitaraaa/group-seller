from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

__all__ = ["Base", "User", "Group", "Order"]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    price: Mapped[float]
    sold: Mapped[bool] = mapped_column(default=False)

    name: Mapped[Optional[str]]
    tag: Mapped[Optional[str]]
    url: Mapped[str] = mapped_column(unique=True)
    founded: Mapped[datetime]
    image: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return (
            f"Group(id = {self.id}, "
            f"name = {self.name}, "
            f"tag = {self.tag}), "
            f"url = {self.url}), "
            f"founded = {self.founded}), "
            f"image = {self.image}), "
            f"price = {self.price}), "
            f"sold = {self.sold}), "
        )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int]
    group_id: Mapped[int]
