from sqlalchemy.orm import Session
from mytimestampsapi import models, schemas
from fastapi_utils.guid_type import GUID


def get_user(db: Session, id: GUID):
    user = db.query(models.User).filter(models.User.id == id).first()
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, offset: int = 0, limit: int = 100):
    users = (
        db.query(models.User)
        .offset(offset)
        .limit(limit)
    )
    return users.all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_timestamps(db: Session, user_id: GUID, offset: int = 0, limit: int = 100):
    user_items = (
        db.query(models.Timestamp)
        .filter(models.Timestamp.user_id == user_id)
        .order_by(models.Timestamp.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return user_items


def create_user_timestamps(db: Session, user_id: GUID, timestamp: schemas.TimestampCreate):
    db_timestamp = models.Timestamp(**timestamp.dict(), user_id=user_id)
    db.add(db_timestamp)
    db.commit()
    db.refresh(db_timestamp)
    return db_timestamp
