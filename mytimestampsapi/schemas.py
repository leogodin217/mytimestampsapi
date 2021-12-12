from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime


class LogMessageBase(BaseModel):
    user_id: UUID
    log_message: str


class LogMessageCreate(LogMessageBase):
    pass


class LogMessage(LogMessageBase):
    id: UUID
    timestamp: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: UUID
    log_messages: List[LogMessage] = []

    class Config:
        orm_mode = True
