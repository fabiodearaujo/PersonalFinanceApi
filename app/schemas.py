from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    class Config:
        orm_mode = True


class UserUpdatePassword(BaseModel):
    password: str
    new_password: str

    class Config:
        orm_mode = True


class TransactionBase(BaseModel):
    user_id: int
    transaction_name: str
    transaction_category: str
    transaction_type: str
    transaction_value: float
    transaction_date: date
    account_type: str


class TransactionCreate(TransactionBase):
    class Config:
        orm_mode = True


class TransactionUpdate(BaseModel):
    transaction_name: Optional[str] = None
    transaction_category: Optional[str] = None
    transaction_type: Optional[str] = None
    transaction_value: Optional[float] = None
    transaction_date: Optional[date] = None
    account_type: Optional[str] = None

    class Config:
        orm_mode = True


class SuggestionBase(BaseModel):
    category: str
    description: str


class SuggestionCreate(SuggestionBase):
    class Config:
        orm_mode = True


class SuggestionUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True
