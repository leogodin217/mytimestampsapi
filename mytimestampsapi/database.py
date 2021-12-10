from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DEFAULT_DATABASE_URL = "postgresql://mytimestamps:mytimestamps@localhost/mytimestamps"
SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL', DEFAULT_DATABASE_URL)


engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
