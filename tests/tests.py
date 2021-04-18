import asyncio
import pytest
from starlette.testclient import TestClient
from starlette.status import *
from run import app, connect_db, disconnect_db
from utils.db import execute, fetch

client = TestClient(app)
loop = asyncio.get_event_loop()

username = "admin"
password = "123"
new_user_id, new_movie_id = None, None

@pytest.fixture(scope='session', autouse=True)
def db_conn():
    # Will be executed before the first test
    db = loop.run_until_complete(connect_db())
    yield db
    # Will be executed after the last test
    loop.run_until_complete(disconnect_db(db))


def db_delete_user(username):
    query = """ delete from users where username = :username; """
    loop.run_until_complete(execute(query, is_many=False, values={"username": username}))
    return


def login(username, password):
    response = client.post("/login", data={
        "username": username,
        "password": password,
    })
    return response

def get_auth_header(username, password):
    response = login(username, password)
    jwt_token = response.json()['access_token']
    auth_header = {"Authorization": f"Bearer {jwt_token}"}
    return auth_header


def test_login_successful():
    response = login(username, password)
    assert response.status_code == HTTP_200_OK
    assert "access_token" in response.json()


def test_login_unsuccessful():
    response = login(username, "wrong-password")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert "access_token" not in response.json()


def test_post_user():
    user_dict = {
        "username": "test-user",
        "password": "test-password",
        "email": "test@email.com",
        "role": "personal"
    }
    # Delete user if exists
    db_delete_user(user_dict['username'])

    # Create user
    response = client.post("/v1/users", json=user_dict)
    assert response.status_code == HTTP_201_CREATED
    global new_user_id
    new_user_id = response.json().get('id')

    # Assert that user already exists
    response = client.post("/v1/users", json=user_dict)
    assert response.status_code == HTTP_400_BAD_REQUEST


def test_patch_user():
    auth_header = get_auth_header(username, password)
    patch_dict = {
        "value": "personal"
    }

    response = client.patch(f"/v1/users/{new_user_id}/role", json=patch_dict, headers=auth_header)
    assert response.status_code == HTTP_200_OK
    assert response.json()['role'] == patch_dict['value']


def test_get_user():
    auth_header = get_auth_header(username, password)
    response = client.get(f"/v1/users/{new_user_id}", headers=auth_header)
    assert response.status_code == HTTP_200_OK
    assert 'username' in response.json()


def test_post_movie():
    auth_header = get_auth_header(username, password)
    user_dict = {
        "title": "Test Movie!",
        "description": "Example movie complete description.",
        "stock": 3,
        "rental_price": 7.53,
        "sale_price": 28.60,
        "availability": True
    }
    # Create movie
    response = client.post("/v1/movies", json=user_dict, headers=auth_header)
    assert response.status_code == HTTP_201_CREATED
    assert 'id' in response.json()
    global new_movie_id
    new_movie_id = response.json().get('id')
