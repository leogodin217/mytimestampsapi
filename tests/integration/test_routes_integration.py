from mytimestampsapi.main import app, get_db
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from mytimestampsapi.models import User, LogMessage, Base
import pytest
import sure


# We need to override the DB used by the API. Also, handle deleting test data
# Fortunately, SQLAlchemy and FASTAPI have methods for this. Unfortunately
# This method is slow.
# [TODO] See if we can use one session per test suite and just delete after each test
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
    yield db
    db.rollback()
    db.query(User).delete()
    db.query(LogMessage).delete()
    db.commit()


def db_override():
    engine = create_engine(
        'postgresql://postgres:postgres@localhost/test_mytimestamps')
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()


app.dependency_overrides[get_db] = db_override


@pytest.fixture(scope='module')
def client():
    return TestClient(app)


def test_swagger_path_exists(client):
    response = client.get('/docs')
    response.status_code.should.equal(200)


def test_create_user(client):
    user = {'email': 'me@you.com'}
    created_user = client.post('/users/', json=user)
    created_user.status_code.should.equal(200)
    created_user.json()['email'].should.equal('me@you.com')


def test_get_users(client, db):
    # Create a couple users directly in the DB
    user1 = User(email='me@you.com')
    user2 = User(email='mewithout@you.com')
    db.add(user1)
    db.add(user2)
    db.commit()
    response = client.get('/users/')
    response.status_code.should.equal(200)
    users = response.json()
    print(users)
    users.should.have.length_of(2)
    users[0]['email'].should.equal('me@you.com')
    users[1]['email'].should.equal('mewithout@you.com')
