from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
import os
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = os.environ['SQLALCHEMY_DATABASE_URL']

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_dbSession():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_databases(session):
    result = session.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
    return [row[0] for row in result.fetchall()]


def get_schemas(session):
    result = session.execute(text("SELECT schema_name FROM information_schema.schemata;"))
    return [row[0] for row in result.fetchall()]


def get_tables(session):
    result = session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
    return [row[0] for row in result.fetchall()]
