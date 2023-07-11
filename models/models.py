from datetime import datetime

from sqlalchemy import Column, TIMESTAMP, VARCHAR, Integer, Boolean, Text, ForeignKey, CHAR, BigInteger, SmallInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__: str = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    queries_chat_gpt = Column(Integer, default=3)
    queries_img = Column(Integer, default=1)
    subscription_id = Column(Integer, default=1, nullable=False)


class Subscription(Base):
    __tablename__: str = "subscriptions"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    price = Column(Text, nullable=False)


class Referral(Base):
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="NO ACTION"), nullable=False)
    referral_id = Column(BigInteger, default=True)


