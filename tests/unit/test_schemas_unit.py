from mytimestampsapi.schemas import User, UserBase
from mytimestampsapi.schemas import LogMessage, LogMessageCreate, LogMessageBase
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


def test_user_has_log_messages():
    log_messages = [
        LogMessage(id=uuid4(), user_id=uuid4(),
                   timestamp=datetime.now(), log_message='some message'),
        LogMessage(id=uuid4(), user_id=uuid4(),
                   timestamp=datetime.now(), log_message='some other message'),
    ]
    user = User(id=uuid4(), email='name@foo.com', log_messages=log_messages)
    user.log_messages[0].log_message.should.equal('some message')
    user.log_messages[1].log_message.should.equal('some other message')


def test_logmessage_base_requires_user_id():
    LogMessageBase.when.called_with().should.throw(
        ValueError, re.compile(r'user_id'))


def test_logmessage_base_requires_log_message():
    LogMessageBase.when.called_with().should.throw(
        ValueError, re.compile(r'log_message'))


def test_logmessage_requires_user_id():
    LogMessage.when.called_with().should.throw(ValueError, re.compile(r'user_id'))


def test_logmessage_requires_log_message():
    LogMessage.when.called_with().should.throw(
        ValueError, re.compile(r'log_message'))


def test_logmessage_requires_id():
    LogMessage.when.called_with().should.throw(ValueError, re.compile(r'id\s'))


def test_logmessage_requires_timestamp():
    LogMessage.when.called_with().should.throw(
        ValueError, re.compile(r'timestamp'))
