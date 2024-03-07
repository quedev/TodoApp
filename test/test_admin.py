from starlette import status

from .utils import *
from routers.admin import get_db, get_current_user
from models import Todos

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all_authenticated(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title': 'learn to code!',
                                'description': "It's awesome",
                                'priority': 5,
                                'complete': False,
                                'owner_id': FAKE_ID,
                                'id': FAKE_ID}]


def test_admin_delete_todo(test_todo):
    response = client.delete(f"admin/todo/{FAKE_ID}")
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == FAKE_ID).first()
    assert model is None


def test_admin_delete_todo_not_found(test_todo):
    response = client.delete(f"admin/todo/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found'}