from mytimestampsapi.models import User, LogMessage
import re
import sure


def test_user_requires_email():
    User.when.called_with().should.throw(TypeError, re.compile(r'email'))


def test_user_email_requires_at_sign():
    User.when.called_with(email='namefoocom').should.throw(ValueError)


def test_user_email_requires_name():
    User.when.called_with(email='@foo.com').should.throw(ValueError)


def test_user_email_requires_domain():
    User.when.called_with(email='name@foo').should.throw(ValueError)


def test_user_email_requires_subdomain():
    User.when.called_with(email='name@com').should.throw(ValueError)


def test_valid_email_is_valid():
    User.when.called_with(email='name@foo.com').should_not.throw(Exception)


def test_logmessage_requires_message():
    LogMessage.when.called_with().should.throw(
        TypeError, re.compile('log_message'))


def test_logmessage_requires_user_id():
    LogMessage.when.called_with(log_message='some message').should.throw(
        TypeError, re.compile(r'user_id'))


def test_logmessage_requires_log_message():
    LogMessage.when.called_with(user_id='someid').should.throw(
        TypeError, re.compile(r'log_message'))


def test_logmessage_log_message_limited_to_256_characters():
    message = ''.join(['a' for char in range(256)])
    LogMessage.when.called_with(
        user_id='someid', log_message=message).should_not.throw(Exception)
    message += 'a'
    LogMessage.when.called_with(
        user_id='someid', log_message=message).should.throw(ValueError)
