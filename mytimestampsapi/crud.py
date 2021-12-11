from sqlalchemy.orm import Session
from mytimestampsapi import models, schemas
from fastapi_utils.guid_type import GUID


def get_user(db: Session, user_id: GUID):
    return db.query(models.User).filter(models.User.id == user_id).first()


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


def get_user_logmessages(db: Session, user_id: GUID, offset: int = 0, limit: int = 100):
    user_items = (
        db.query(models.LogMessage)
        .filter(models.LogMessage.user_id == user_id)
        .offset(offset)
        .limit(limit)
        .all()
    ).all()
    return user_items


def create_user_log_messages(db: Session, log_message: schemas.LogMessageCreate, user_id: GUID):
    id = GUID(uuid4())
    db_log_message = models.LogMessage(
        **log_message.dict(), user_id=user_id, id=id)
    db.add(db_log_message)
    db.commit()
    db.refresh(db_log_message)
    return db_log_message
