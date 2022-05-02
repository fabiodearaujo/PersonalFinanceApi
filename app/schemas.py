from datetime import date

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    class Config:
        orm_mode = True


class UserUpdateEmail(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class UserUpdatePassword(BaseModel):
    password: str
    new_password: str

    class Config:
        orm_mode = True


class TransactionBase(BaseModel):
    user_id: int
    transaction_id: int
    transaction_name: str
    transaction_category: str
    transaction_type: str
    transaction_value: float
    transaction_date: date
    account_type: str


class TransactionReturnOne(TransactionBase):
    class Config:
        orm_mode = True


class TransactionCreate(TransactionBase):
    class Config:
        orm_mode = True


class TransactionUpdate(BaseModel):
    transaction_name: str
    transaction_category: str
    transaction_type: str
    transaction_value: float
    transaction_date: date
    account_type: str

    class Config:
        orm_mode = True


class SuggestionBase(BaseModel):
    category: str
    description: str


class SuggestionCreate(SuggestionBase):
    class Config:
        orm_mode = True


class SuggestionUpdate(BaseModel):
    category: str
    description: str

    class Config:
        orm_mode = True
