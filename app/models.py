# necessary imports to setup the models
from .database import Base
from sqlalchemy import Column, ForeignKeyConstraint, Integer, String, Float, Date

# create the User model
class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String)
    

# create the Transaction model
class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    transaction_name = Column(String, nullable=False)
    transaction_category = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    transaction_value = Column(Float, nullable=False)
    transactio_date = Column(Date, nullable=False)
    account_type = Column(String, nullable=False)
    ForeignKeyConstraint(['user_id'], ['users.user_id'])


# create the Suggestion model
class Suggestion(Base):
    __tablename__ = "suggestions"
    suggestion_id = Column(Integer, primary_key=True, nullable=False, index=True)
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
