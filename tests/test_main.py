import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.main import app, get_dbSession
from app.db.models import Base, Subfeddit, Comment
from datetime import datetime

# Configure the test database URL (use PostgreSQL for tests)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_dbSession dependency to use the test database
@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_dbSession] = override_get_db
    client = TestClient(app)
    yield client

# Helper function to clean the database
def clean_db(test_db):
    test_db.query(Comment).delete()
    test_db.query(Subfeddit).delete()
    test_db.commit()

def test_healthcheck(client):
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}

def test_db_conn(client):
    response = client.get("/db-conn")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Database connection successful"}

def test_read_subfeddits(client, test_db):
    clean_db(test_db)
    test_db.add_all([
        Subfeddit(username='userA', title='Technology', description='All about the latest in tech.'),
        Subfeddit(username='userB', title='Books', description='Discuss your favorite books here.'),
        Subfeddit(username='userC', title='Movies', description='Talk about the latest movies.')
    ])
    test_db.commit()

    response = client.get("/subfeddits/")
    assert response.status_code == 200
    assert response.json() == ["Technology", "Movies", "Books"]

def test_read_comments(client, test_db):
    clean_db(test_db)
    subfeddit = Subfeddit(username='userA', title='Technology', description='All about the latest in tech.')
    test_db.add(subfeddit)
    test_db.commit()
    test_db.refresh(subfeddit)

    test_db.add_all([
        Comment(username='user1', text='This is a great tech post!', created_at=datetime.strptime('2024-05-01 12:00:00', '%Y-%m-%d %H:%M:%S'), subfeddit_id=subfeddit.id),
        Comment(username='user2', text='I love the new gadget!', created_at=datetime.strptime('2024-05-02 13:00:00', '%Y-%m-%d %H:%M:%S'), subfeddit_id=subfeddit.id),
        Comment(username='user3', text='This tech is disappointing.', created_at=datetime.strptime('2024-05-03 14:00:00', '%Y-%m-%d %H:%M:%S'), subfeddit_id=subfeddit.id)
    ])
    test_db.commit()

    response = client.get(f"/subfeddit/Technology/comments")
    assert response.status_code == 200
    comments = response.json()
    print(comments)
    assert len(comments) == 3
    assert comments[0]['text'] == 'This tech is disappointing.'
    assert 'polarity' in comments[0]
    assert 'classification' in comments[0]

def test_read_comments_with_filters(client, test_db):
    response = client.get(f"/subfeddit/Technology/comments?start_time=2024-05-02T00:00:00&end_time=2024-05-03T23:59:59")
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 2

    response = client.get(f"/subfeddit/Technology/comments?sort_by_polarity=True")
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 3
    assert comments[0]['polarity'] >= comments[1]['polarity']
