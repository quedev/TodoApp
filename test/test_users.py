from starlette import status

from .utils import *
from routers.users import get_current_user, get_db
from models import Users

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'hamed'
    assert response.json()['email'] == 'hamed@quedev.com'
    assert response.json()['first_name'] == 'Hamed'
    assert response.json()['last_name'] == 'Abbaszadeh'
    assert response.json()['role'] == 'admin'
    

def test_change_password_success(test_user):
    response = client.put("/users/change_password",
                          json={"password": 'testpassword', "new_password": "newpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_passsword_invalid_current_password(test_user):
    response = client.put("/users/change_password",
                          json={"password": 'wrongpassword', "new_password": "newpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Current password is not correct'}
