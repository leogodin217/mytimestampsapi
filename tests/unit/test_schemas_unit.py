from mytimestampsapi.schemas import User, UserBase
from mytimestampsapi.schemas import Timestamp, TimestampCreate, TimestampBase
from uuid import uuid4
from datetime import datetime
import re
import sure


def test_user_base_requires_email():
    UserBase.when.called_with().should.throw(ValueError)


def test_user_requires_email():
    User.when.called_with().should.throw(ValueError, re.compile(r'email'))


def test_user_requires_id():
    User.when.called_with().should.throw(ValueError, re.compile(r'id\s'))


def test_user_has_timestamps():
    timestamps = [
        Timestamp(id=uuid4(), user_id=uuid4(),
                  timestamp=datetime.now(), message='some message'),
        Timestamp(id=uuid4(), user_id=uuid4(),
                  timestamp=datetime.now(), message='some other message'),
    ]
    user = User(id=uuid4(), email='name@foo.com', timestamps=timestamps)
    user.timestamps[0].message.should.equal('some message')
    user.timestamps[1].message.should.equal('some other message')


def test_timestamp_base_requires_user_id():
    TimestampBase.when.called_with().should.throw(
        ValueError, re.compile(r'user_id'))


def test_timestamp_base_requires_message():
    TimestampBase.when.called_with().should.throw(
        ValueError, re.compile(r'message'))


def test_timestamp_requires_user_id():
    Timestamp.when.called_with().should.throw(ValueError, re.compile(r'user_id'))


def test_timestamp_requires_message():
    Timestamp.when.called_with().should.throw(
        ValueError, re.compile(r'message'))


def test_timestamp_requires_id():
    Timestamp.when.called_with().should.throw(ValueError, re.compile(r'id\s'))


def test_timestamp_requires_timestamp():
    Timestamp.when.called_with().should.throw(
        ValueError, re.compile(r'timestamp'))
