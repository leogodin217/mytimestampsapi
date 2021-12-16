from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm.session import sessionmaker
from mytimestampsapi.database import SessionLocal
from mytimestampsapi.schemas import UserCreate, LogMessageCreate
from mytimestampsapi.models import User, LogMessage, Base
from mytimestampsapi.crud import create_user, get_user, get_users, get_user_by_email
from mytimestampsapi.crud import create_user_log_messages, get_user_logmessages
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


def test_create_log_message(db):
    user_schema = UserCreate(email='name@foo.com')
    user = create_user(db=db, user=user_schema)
    log_message_schema = LogMessageCreate(
        log_message='test logmessage', user_id=user.id)
    log_message = create_user_log_messages(
        db=db, log_message=log_message_schema)
    log_message.log_message.should.equal('test logmessage')
    log_message.id.should.be.a(UUID)
    log_message.timestamp.should.be.a(datetime)


def test_get_user_logmessages_handles_offset_and_limit(db):
    user_schema = UserCreate(email='name@foo.com')
    user = create_user(db=db, user=user_schema)
    new_log_messages = []
    for index in range(10):
        # Make sure we have a different timestamp
        time.sleep(.1)
        log_message_schema = LogMessageCreate(
            log_message='test logmessage' + str(index), user_id=user.id)
        log_message = create_user_log_messages(
            db=db, log_message=log_message_schema)
        new_log_messages.append(log_message)

    log_messages = get_user_logmessages(
        db=db, user_id=user.id, offset=3, limit=2)
    log_messages.should.have.length_of(2)
    # log messages are returned in reverse timestamp order
    log_messages[0].log_message.should.equal('test logmessage6')
    log_messages[1].log_message.should.equal('test logmessage5')


def test_get_user_logmessages_returns_logmessages_in_reverse_time_order(db):
    user_schema = UserCreate(email='name@foo.com')
    user = create_user(db=db, user=user_schema)
    new_log_messages = []
    for index in range(10):
        # Make sure we have a different timestamp
        time.sleep(.1)
        log_message_schema = LogMessageCreate(
            log_message='test logmessage' + str(index), user_id=user.id)
        log_message = create_user_log_messages(
            db=db, log_message=log_message_schema)
        new_log_messages.append(log_message)
    log_messages = get_user_logmessages(
        db=db, user_id=user.id)
    log_messages.should.have.length_of(10)
    log_messages[0].log_message.should.equal('test logmessage9')
    log_messages[1].log_message.should.equal('test logmessage8')
    log_messages[2].log_message.should.equal('test logmessage7')
    log_messages[3].log_message.should.equal('test logmessage6')
    log_messages[4].log_message.should.equal('test logmessage5')
    log_messages[5].log_message.should.equal('test logmessage4')
    log_messages[6].log_message.should.equal('test logmessage3')
    log_messages[7].log_message.should.equal('test logmessage2')
    log_messages[8].log_message.should.equal('test logmessage1')
    log_messages[9].log_message.should.equal('test logmessage0')


def test_get_user_logmessages_only_returns_the_users_log_messages(db):
    user1_schema = UserCreate(email='name1@foo.com')
    user1 = create_user(db=db, user=user1_schema)
    create_user_log_messages(
        db=db, log_message=LogMessageCreate(
            user_id=user1.id, log_message='user 1 message 1')
    )
    user2_schema = UserCreate(email='name2@foo.com')
    user2 = create_user(db=db, user=user2_schema)
    create_user_log_messages(
        db=db, log_message=LogMessageCreate(
            user_id=user2.id, log_message='user 2 message 1')
    )
    log_messages = get_user_logmessages(db=db, user_id=user1.id)
    log_messages.should.have.length_of(1)
    log_messages[0].log_message.should.equal('user 1 message 1')
