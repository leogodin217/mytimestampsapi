from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm.session import sessionmaker
from mytimestampsapi.database import SessionLocal
from mytimestampsapi.models import User, LogMessage, Base
import pytest
import re
from uuid import UUID
import sure


@pytest.fixture(scope='module')
def session():
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
    session = SessionLocal()
    yield session
    print('Closing stuff')
    session.rollback()
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def db(session):
    db = session
    db.begin()
    yield db
    db.rollback()


# Make sure we can save a User
def test__valid_user_create(db):
    user = User(email='name2@foo.com')
    db.add(user)
    db.flush()
    db.refresh(user)
    user.id.should.be.a(UUID)
    user.id.hex.should.have.length_of(32)
