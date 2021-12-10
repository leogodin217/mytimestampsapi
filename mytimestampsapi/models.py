from datetime import datetime
from typing_extensions import Required
from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null
from fastapi_utils.guid_type import GUID
from uuid import uuid4
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, index=True, default=uuid4)
    email = Column(String, unique=True, index=True, nullable=False)

    log_messages = relationship("LogMessage")


class LogMessage(Base):
    __tablename__ = "log_messages"

    id = Column(GUID, primary_key=True, index=True, default=uuid4)
    user_id = Column(GUID, ForeignKey('users.id'), index=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    log_message = Column(String(256), nullable=False)
