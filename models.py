from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base
from sqlalchemy import UniqueConstraint

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100), nullable=True)
    full_name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    group_memberships = relationship(
        "GroupMember",
        back_populates="user"
    )


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_chat_id = Column(BigInteger, unique=True, nullable=False)
    group_name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship(
        "GroupMember",
        back_populates="group"
    )


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, autoincrement=True)

    group_id = Column(
        Integer,
        ForeignKey("groups.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    joined_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "user_id",
            name="unique_group_user"
        ),
    )

    group = relationship(
        "Group",
        back_populates="members"
    )

    user = relationship(
        "User",
        back_populates="group_memberships"
    )

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    group_id = Column(
        Integer,
        ForeignKey("groups.id"),
        nullable=False
    )

    paid_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(
        String(200),
        nullable=False
    )

    amount = Column(
        Integer,
        nullable=False
    )

    split_type = Column(
        String(20),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    shares = relationship(
        "ExpenseShare",
        back_populates="expense"
    )

    group = relationship("Group")
    paid_by = relationship("User")

class ExpenseShare(Base):
    __tablename__ = "expense_shares"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    expense_id = Column(
        Integer,
        ForeignKey("expenses.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    amount = Column(
        Integer,
        nullable=False
    )

    expense = relationship(
        "Expense",
        back_populates="shares"
    )

  #  expense = relationship("Expense")
    user = relationship("User")


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True)

    group_id = Column(
        Integer,
        ForeignKey("groups.id"),
        nullable=False
    )

    from_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    to_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    amount = Column(
        Integer,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )