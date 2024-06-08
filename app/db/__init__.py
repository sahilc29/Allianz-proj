from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = os.environ['SQLALCHEMY_DATABASE_URL']

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_dbSession():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()


def get_tables(session):
    result = session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
    return [row[0] for row in result.fetchall()]
