from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base
from main import app
from routers.todos import get_db, get_current_user
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from models import Todos

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"
FAKE_ID = 1

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autoflush=False,
                                   autocommit=False,
                                   bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_curren_user():
    return {'username': 'hamed',
            'id': FAKE_ID,
            'user_role': 'admin'}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_curren_user

client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title='learn to code!',
        description="It's awesome",
        priority=5,
        complete=False,
        owner_id=FAKE_ID
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.commit()


def test_read_all_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title': 'learn to code!',
                                'description': "It's awesome",
                                'priority': 5,
                                'complete': False,
                                'owner_id': FAKE_ID,
                                'id': FAKE_ID}]
