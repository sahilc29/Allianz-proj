from pathlib import Path
import sys
import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
import uvicorn
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError
from app.db import engine, Base, get_dbSession
from app.api.models.CommentResponse import CommentResponse
from app.db.models import Comment, Subfeddit
from datetime import datetime
from app.db.repository import get_subfeddits, get_recent_comments
from app.data.insert_data import DataIngest
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pydantic import BaseModel


PACKAGE_ROOT = Path(os.path.abspath(os.path.dirname(__file__))).parent
sys.path.append(str(PACKAGE_ROOT))


class HealthCheckResponse(BaseModel):
    status: str
    version: str


# Initialize the FastAPI app
app = FastAPI()
analyzer = SentimentIntensityAnalyzer()


def check_tables_exist(engine):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return 'comments' in tables and 'subfeddits' in tables


def insert_initial_data(db):
    # Check if any data exists in the subfeddits table
    subfeddit_count = db.query(Subfeddit).count()

    # Insert initial data if no rows exist
    if subfeddit_count == 0:
        DataIngest().subfeddits()

    # Check if any data exists in the comments table
    comment_count = db.query(Comment).count()
    if comment_count == 0:
        DataIngest().comments()


def analyze_sentiment(text: str):
    score = analyzer.polarity_scores(text)['compound']
    classification = "positive" if score >= 0 else "negative"
    return score, classification


@app.get("/", include_in_schema=False, response_class=HTMLResponse)
def root():
    html_content = """
    <html>
        <head>
            <title>Feddit API</title>
        </head>
        <body>
            <h1>Welcome to the Feddit API</h1>
            <p>To know more about the Feddit API, <a href="/docs">click here</a>.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/db-conn")
def dbhealthcheck(db: Session = Depends(get_dbSession)):
    try:
        # Try a simple database operation
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection failed: {}".format(e))


@app.get("/api/v1/version", response_model=HealthCheckResponse)
def healthcheck():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/subfeddits/", response_model=List[str])
def read_subfeddits(db: Session = Depends(get_dbSession)):
    subfeddits = get_subfeddits(db)
    if not subfeddits:
        raise HTTPException(status_code=404, detail="No subfeddits found")
    return [title[0] for title in subfeddits]


@app.get("/subfeddit/{subfeddit_name}/comments", response_model=List[CommentResponse])
def read_comments(
    subfeddit_name: str,
    limit: int = Query(default=25),
    db=Depends(get_dbSession),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    sort_by_polarity: bool = Query(False)
):
    subfeddit_id = db.query(Subfeddit).filter(Subfeddit.title == subfeddit_name).first()
    if subfeddit_id is None:
        raise HTTPException(status_code=404, detail='Subfeddit not found')
    query = db.query(Comment).filter(Comment.subfeddit_id == subfeddit_id.id)

    if start_time:
        query = query.filter(Comment.created_at >= start_time)
    if end_time:
        query = query.filter(Comment.created_at <= end_time)

    if start_time is None and end_time is None:
        if sort_by_polarity:
            comments = get_recent_comments(db, subfeddit_id.id, limit)
            comments = sorted(comments, key=lambda x: analyze_sentiment(x.text)[0], reverse=True)
        else:
            comments = get_recent_comments(db, subfeddit_id.id, limit)
    elif start_time is not None and end_time is not None:
        if sort_by_polarity:
            comments = query.all()
            comments = sorted(comments, key=lambda x: analyze_sentiment(x.text)[0], reverse=True)
        else:
            comments = query.all()
    else:
        comments = get_recent_comments(db, subfeddit_id.id, limit)

    response = []
    for comment in comments[:limit]:
        score, classification = analyze_sentiment(comment.text)
        response.append({
            'id': comment.id,
            'text': comment.text,
            'polarity': score,
            'classification': classification
        })
    return response


def main():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    if not check_tables_exist(engine):
        Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        insert_initial_data(db)
    except IntegrityError:
        db.rollback()
    finally:
        db.close()

    uvicorn.run(app, host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
