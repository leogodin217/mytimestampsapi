from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm.session import sessionmaker
from mytimestampsapi.database import SessionLocal
from mytimestampsapi.models import User, LogMessage, Base
import pytest
import re
import sure


@pytest.fixture(autouse=True, scope='module')
def db():
    '''Create the database and setup tables'''
    print('Setting things up')
    engine = create_engine(
        'postgresql://postgres:postgres@localhost/test_mytimestamps')
    if not database_exists(engine.url):
        create_database(engine.url)
    # Create the tablese
    Base.metadata.create_all(engine)
    # Start a session and transaction
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    db.begin()
    yield db
    Base.metadata.drop_all(engine)
    db.close()


# Make sure we can save a User
def test_user_email_is_valid_email(db):
    # User(email='asdf').should.throw(ValueError, 'Invalid Email')
    User.when.called_with(email='adsfasd').should.throw(ValueError)
    db.add(User(email='name@foo.com'))
    db.commit()
