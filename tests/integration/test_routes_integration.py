from mytimestampsapi.main import app, get_db
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from mytimestampsapi.models import User, Timestamp, Base
from datetime import date, time
import arrow
from uuid import uuid4
import pytest
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
    yield db
    db.rollback()
    db.query(Timestamp).delete()
    db.query(User).delete()
    db.commit()
    db.close()

# This overrides the DB used by the app.


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


def test_get_user(client, db):
    user1 = User(email='me@you.com')
    db.add(user1)
    db.commit()
    url = f'/users/{str(user1.id)}'
    response = client.get(url)
    response.status_code.should.equal(200)


def test_get_invalid_user_returns_404(client):
    user_id = str(uuid4())
    response = client.get(f'/users/{user_id}')
    response.status_code.should.equal(404)


def test_create_timestamp(client, db):
    user = User(email='me@you.com')
    db.add(user)
    db.commit()
    timestamp_data = {'message': 'a message', 'user_id': str(user.id)}
    response = client.post(
        f'/users/{str(user.id)}/timestamps/', json=timestamp_data)
    print(response.json())
    response.status_code.should.equal(200)
    response.json()['user_id'].should.equal(str(user.id))
    response.json()['message'].should.equal('a message')
    timestamp = arrow.get(response.json()['timestamp'])
    timestamp.date().should.be.a(date)
    timestamp.time().should.be.a(time)
