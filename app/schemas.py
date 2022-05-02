from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    
    class Config:
        orm_mode = True


class UserUpdate(UserBase):
    email: Optional[EmailStr]
    password: Optional[str]

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
   
    class Config:
        orm_mode = True


class SuggestionUpdate(SuggestionBase):
    category: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True
