from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from mytimestampsapi import crud, models, schemas
from mytimestampsapi.database import SessionLocal, engine
from uuid import UUID

app = FastAPI()

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db), offset: int = 0, limit: int = 100):
    users = crud.get_users(db, offset=offset, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = crud.get_user(db=db, id=UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users/{user_id}/timestamps/", response_model=schemas.Timestamp)
def create_user_timestamp(user_id: UUID, timestamp: schemas.TimestampCreate, db: Session = Depends(get_db)):
    return crud.create_user_timestamps(db=db, timestamp=timestamp, user_id=user_id)
