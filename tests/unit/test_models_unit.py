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
