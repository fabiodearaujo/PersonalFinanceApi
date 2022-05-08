from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    class Config:
        orm_mode = True


class UserUpdateEmail(BaseModel):
    user_id: int
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class UserUpdatePassword(BaseModel):
    user_id: int
    password: str
    new_password: str

    class Config:
        orm_mode = True


class UserDelete(BaseModel):
    user_id: int
    password: str
    confirm: bool = True

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


class TransactionGetOne(BaseModel):
    transaction_id: int

    class Config:
        orm_mode = True


class TransactionCreate(TransactionBase):
    class Config:
        orm_mode = True


class TransactionUpdate(BaseModel):
    transaction_id: int
    transaction_name: str
    transaction_category: str
    transaction_type: str
    transaction_value: float
    transaction_date: date
    account_type: str

    class Config:
        orm_mode = True


class TransactionDelete(BaseModel):
    transaction_id: int
    confirm: bool = True

    class Config:
        orm_mode = True


class MoveFunds(BaseModel):
    user_id: int
    transaction_value: float
    transaction_date: date
    account_type: str

    class Config:
        orm_mode = True


class SuggestionBase(BaseModel):
    category: str
    description: str


class SuggestionGetOne(BaseModel):
    suggestion_id: int

    class Config:
        orm_mode = True


class SuggestionCreate(SuggestionBase):
    class Config:
        orm_mode = True


class SuggestionUpdate(BaseModel):
    suggestion_id: int
    category: str
    description: str

    class Config:
        orm_mode = True


class SuggestionDelete(BaseModel):
    suggestion_id: int
    confirm: bool = True

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
