from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

from uvicorn import Config


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class UserUpdate(UserBase):
    email: Optional[EmailStr]
    password: Optional[str]

    class Config:
        orm_mode = True


class TransactionBase(BaseModel):
    transaction_name: str
    transaction_category: str
    transaction_type: str
    transaction_value: float
    transaction_date: date
    account_type: str


class TransactionCreate(TransactionBase):
    transaction_name: str
    transaction_category: str
    transaction_type: str
    transaction_value: float
    transaction_date: date
    account_type: str

    class Config:
        orm_mode = True


class TransactionUpdate(TransactionBase):
    transaction_name: Optional[str]
    transaction_category: Optional[str]
    transaction_type: Optional[str]
    transaction_value: Optional[float]
    transaction_date: Optional[date]
    account_type: Optional[str]

    class Config:
        orm_mode = True


class SuggestionBase(BaseModel):
    category: str
    description: str


class SuggestionCreate(SuggestionBase):
    category: str
    description: str

    class Config:
        orm_mode = True


class SuggestionUpdate(SuggestionBase):
    category: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True
