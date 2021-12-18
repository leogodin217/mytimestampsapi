from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm.session import sessionmaker
from mytimestampsapi.database import SessionLocal
from mytimestampsapi.schemas import UserCreate, TimestampCreate
from mytimestampsapi.models import User, Timestamp, Base
from mytimestampsapi.crud import create_user, get_user, get_users, get_user_by_email
from mytimestampsapi.crud import create_user_timestamps, get_user_timestamps
from datetime import datetime
import pytest
import re
from uuid import UUID
from datetime import datetime
import time
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
    db.query(Timestamp).delete()
    db.query(User).delete()
    db.commit()


def test_create_user(db):
    user_schema = UserCreate(email='name@foo.com')
    user = create_user(db=db, user=user_schema)
    user.id.should.be.a(UUID)
    user.email.should.equal('name@foo.com')
    user.timestamps.should.be.empty


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


def test_get_user_lazy_loads_timestamps(db):
    user = User(email='name@foo.com')
    db.add(user)
    db.commit()
    timestamp1 = Timestamp(user_id=user.id, message='a message')
    timestamp2 = Timestamp(user_id=user.id, message='another message')
    db.add(timestamp1)
    db.add(timestamp2)
    db.commit()
    user_found = get_user(db=db, id=user.id)
    print(user)
    # If we access timestamps it will load them,so we need to inspect the dict
    # user_get.timestamps.should.have.length_of(0)
    user_found.__dict__.should.have.key('email')
    user_found.__dict__.should_not.have.key('timestamps')
    # Now when we access log messages, they should be there
    user_found.timestamps.should.have.length_of(2)


def test_get_user_by_email(db):
    user_schema = UserCreate(email='name@foo.com')
    user = create_user(db=db, user=user_schema)
    user2_schema = UserCreate(email='name2@foo.com')
    user2 = create_user(db=db, user=user2_schema)
    user_found = get_user_by_email(db=db, email=user.email)
    user_found.id.should.equal(user.id)


def test_create_timestamp(db):
    user_schema = UserCreate(email='name@foo.com')
    user = create_user(db=db, user=user_schema)
    timestamp_schema = TimestampCreate(
        message='test Timestamp', user_id=user.id)
    timestamp = create_user_timestamps(
        db=db, timestamp=timestamp_schema)
    timestamp.message.should.equal('test Timestamp')
    timestamp.id.should.be.a(UUID)
    timestamp.timestamp.should.be.a(datetime)


def test_get_user_timestamps_handles_offset_and_limit(db):
    user_schema = UserCreate(email='name@foo.com')
    user = create_user(db=db, user=user_schema)
    new_timestamps = []
    for index in range(10):
        # Make sure we have a different timestamp
        time.sleep(.1)
        timestamp_schema = TimestampCreate(
            message='test Timestamp' + str(index), user_id=user.id)
        timestamp = create_user_timestamps(
            db=db, timestamp=timestamp_schema)
        new_timestamps.append(timestamp)

    timestamps = get_user_timestamps(
        db=db, user_id=user.id, offset=3, limit=2)
    timestamps.should.have.length_of(2)
    # log messages are returned in reverse timestamp order
    timestamps[0].message.should.equal('test Timestamp6')
    timestamps[1].message.should.equal('test Timestamp5')


def test_get_user_timestamps_returns_timestamps_in_reverse_time_order(db):
    user_schema = UserCreate(email='name@foo.com')
    user = create_user(db=db, user=user_schema)
    new_timestamps = []
    for index in range(10):
        # Make sure we have a different timestamp
        time.sleep(.1)
        timestamp_schema = TimestampCreate(
            message='test Timestamp' + str(index), user_id=user.id)
        timestamp = create_user_timestamps(
            db=db, timestamp=timestamp_schema)
        new_timestamps.append(timestamp)
    timestamps = get_user_timestamps(
        db=db, user_id=user.id)
    timestamps.should.have.length_of(10)
    timestamps[0].message.should.equal('test Timestamp9')
    timestamps[1].message.should.equal('test Timestamp8')
    timestamps[2].message.should.equal('test Timestamp7')
    timestamps[3].message.should.equal('test Timestamp6')
    timestamps[4].message.should.equal('test Timestamp5')
    timestamps[5].message.should.equal('test Timestamp4')
    timestamps[6].message.should.equal('test Timestamp3')
    timestamps[7].message.should.equal('test Timestamp2')
    timestamps[8].message.should.equal('test Timestamp1')
    timestamps[9].message.should.equal('test Timestamp0')


def test_get_user_timestamps_only_returns_the_users_timestamps(db):
    user1_schema = UserCreate(email='name1@foo.com')
    user1 = create_user(db=db, user=user1_schema)
    create_user_timestamps(
        db=db, timestamp=TimestampCreate(
            user_id=user1.id, message='user 1 message 1')
    )
    user2_schema = UserCreate(email='name2@foo.com')
    user2 = create_user(db=db, user=user2_schema)
    create_user_timestamps(
        db=db, timestamp=TimestampCreate(
            user_id=user2.id, message='user 2 message 1')
    )
    timestamps = get_user_timestamps(db=db, user_id=user1.id)
    timestamps.should.have.length_of(1)
    timestamps[0].message.should.equal('user 1 message 1')
