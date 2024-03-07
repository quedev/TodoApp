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


def test_read_one_authenticated(test_todo):
    response = client.get(f"/todo/{FAKE_ID}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'title': 'learn to code!',
                               'description': "It's awesome",
                               'priority': 5,
                               'complete': False,
                               'owner_id': FAKE_ID,
                               'id': FAKE_ID}


def test_read_one_authenticated_not_found():
    response = client.get("/todo/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo id not found'}


def test_create_todo(test_todo):
    request_data = {
        'title': 'New Todo!',
        'description': 'New todo description',
        'priority': 5,
        'complete': False,
    }

    response = client.post('/todo', json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_update_todo(test_todo):
    request_data = {
        'title': 'Change the title of the todo already saved!',
        'description': "It's awesome",
        'priority': 5,
        'complete': False,
    }

    response = client.put(f'todo/{FAKE_ID}', json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == FAKE_ID).first()
    assert model.title == request_data.get('title')


def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Change the title of the todo already saved!',
        'description': "It's awesome",
        'priority': 5,
        'complete': False,
    }

    response = client.put(f'todo/999', json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found'}


def test_delete_todo(test_todo):
    response = client.delete(f'/todo/{FAKE_ID}')
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == FAKE_ID).first()
    assert model is None


def test_delete_todo_not_found(test_todo):
    response = client.delete(f'/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found'}
