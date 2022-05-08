# necessary imports to setup the models
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String

from .database import Base


# create the User model
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)


# create the Transaction model
class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_name = Column(String, nullable=False)
    transaction_category = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    transaction_value = Column(Float, nullable=False)
    transaction_date = Column(Date, nullable=False)
    account_type = Column(String, nullable=False)


# create the Suggestion model
class Suggestion(Base):
    __tablename__ = "suggestions"
    suggestion_id = Column(Integer, primary_key=True, nullable=False, index=True)
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
