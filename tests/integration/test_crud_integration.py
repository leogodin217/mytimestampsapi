from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm.session import sessionmaker
from mytimestampsapi.database import SessionLocal
from mytimestampsapi.schemas import UserCreate, LogMessageCreate
from mytimestampsapi.models import User, LogMessage, Base
from mytimestampsapi.crud import create_user, get_user, get_users, get_user_by_email
from datetime import datetime
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
    # db.begin()
    yield db
    db.rollback()
    db.query(LogMessage).delete()
    db.query(User).delete()
    db.commit()


def test_create_user(db):
    user_schema = UserCreate(email='name@foo.com')
    user = create_user(db=db, user=user_schema)
    user.id.should.be.a(UUID)
    user.email.should.equal('name@foo.com')
    user.log_messages.should.be.empty


def test_get_users(db):
    user_schema = UserCreate(email='name3@foo.com')
    user = create_user(db=db, user=user_schema)
    user2_schema = UserCreate(email='name2@foo.com')
    user2 = create_user(db=db, user=user2_schema)
    users = get_users(db=db)
    users.should.have.length_of(2)
    users[0].email.should.equal('name3@foo.com')
    users[1].email.should.equal('name2@foo.com')


def test_get_user(db):
    user_schema = UserCreate(email='name@foo.com')
    user = create_user(db=db, user=user_schema)
    user2_schema = UserCreate(email='name2@foo.com')
    user2 = create_user(db=db, user=user2_schema)
    user_found = get_user(db=db, id=user.id)
    user_found.email.should.equal('name@foo.com')


def test_get_user_by_email(db):
    user_schema = UserCreate(email='name@foo.com')
    user = create_user(db=db, user=user_schema)
    user2_schema = UserCreate(email='name2@foo.com')
    user2 = create_user(db=db, user=user2_schema)
    user_found = get_user_by_email(db=db, email=user.email)
    user_found.id.should.equal(user.id)
