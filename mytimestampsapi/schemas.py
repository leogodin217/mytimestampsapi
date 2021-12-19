from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime


class TimestampBase(BaseModel):
    message: str


class TimestampCreate(TimestampBase):
    pass


class Timestamp(TimestampBase):
    id: UUID
    user_id: UUID
    timestamp: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: UUID
    timestamps: List[Timestamp] = []

    class Config:
        orm_mode = True
