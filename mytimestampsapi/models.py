from datetime import datetime
from typing_extensions import Required
from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, Enum, DateTime
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql.expression import null
from fastapi_utils.guid_type import GUID
from uuid import uuid4
from mytimestampsapi.database import Base
import re

# Enable GUID caching in the DB
# See https://docs.sqlalchemy.org/en/14/core/custom_types.html#sqlalchemy.types.TypeDecorator.cache_ok
cached_guid = GUID
cached_guid.cache_ok = True


class User(Base):
    # Adding __init__ allows us to unit test required fields that skip
    # validators when not passed in.
    def __init__(self, email):
        self.email = email

    __tablename__ = "users"

    id = Column(cached_guid, primary_key=True, index=True, default=uuid4)
    email = Column(String, unique=True, index=True,
                   nullable=False, default='none')

    timestamps = relationship("Timestamp", lazy='select')

    def __repr__(self):
        return f'<User(id={self.id}, email={self.email})>'

    @validates('email')
    def validate_email(self, key, email):
        # https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
        if not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            raise ValueError('Invalid email')
        return email


class Timestamp(Base):
    # Adding __init__ allows us to unit test required fields that skip
    # validators when not passed in.
    def __init__(self, user_id, message):
        self.user_id = user_id
        self.message = message

    __tablename__ = "timestamps"

    id = Column(cached_guid, primary_key=True, index=True, default=uuid4)
    user_id = Column(GUID, ForeignKey('users.id'), index=True, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    message = Column(String(256), nullable=False)

    def __repr__(self):
        return f'<Timestamp(id={self.id}, user_id={self.user_id}, message={self.message}, timestamp={self.timestamp})>'

    @validates('message')
    def validate_timestamp(self, key, message):
        if len(message) > 256:
            raise ValueError(
                'Message cannot be greater than 256 characters')
        return message
