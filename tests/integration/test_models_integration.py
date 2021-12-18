from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm.session import sessionmaker
from mytimestampsapi.database import SessionLocal
from mytimestampsapi.models import User, Timestamp, Base
from datetime import datetime
import pytest
import re
from uuid import UUID
import sure


@pytest.fixture(scope='module')
def session():
    '''Create the database and setup tables'''
    print('Setting things up')
    db_url = 'postgresql://postgres:postgres@localhost/test_mytimestamps'
    engine = create_engine(db_url)
    if not database_exists(db_url):
        create_database(db_url)
    # Create the tablese
    Base.metadata.create_all(engine)
    # Start a session and transaction
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    print('Closing stuff')
    session.rollback()
    session.close()
    Base.metadata.drop_all(engine)


@ pytest.fixture(autouse=True)
def db(session):
    db = session
    db.begin()
    yield db
    db.rollback()


# Make sure we can save a User
def test_valid_user_create(db):
    user = User(email='name2@foo.com')
    db.add(user)
    db.flush()
    db.refresh(user)
    user.id.should.be.a(UUID)
    user.id.hex.should.have.length_of(32)


# Make sure we can save a Timestamp
def test_valid_timestamp_create(db):
    user = User(email='name@foo.com')
    db.add(user)
    db.flush()
    db.refresh(user)
    timestamp = Timestamp(user_id=user.id, message='some message')
    db.add(timestamp)
    db.flush()
    db.refresh(timestamp)
    timestamp.id.should.be.a(UUID)
    timestamp.timestamp.should.be.a(datetime)
