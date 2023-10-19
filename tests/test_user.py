from app import create_app
from http import HTTPStatus
from models import UserModel


def test_register() -> None:
    flask_app = create_app()

    with flask_app.test_client() as client:
        test_json = {
            "username": "test-user",
            "email": "dummy-email@yahoo.com",
            "password": "test-password",
        }
        response = client.post("/register", json=test_json)
        response_data = response.get_json()
        assert response_data["message"] == "User created successfully."
        assert response.status_code == HTTPStatus.CREATED


def test_login() -> None:
    flask_app = create_app()
    with flask_app.test_client() as client:
        test_json = {"username": "test-user", "password": "test-password"}
        response = client.post("/login", json=test_json)
        response_data = response.get_json()
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response.status_code == HTTPStatus.OK


def test_get_user() -> None:
    flask_app = create_app()
    with flask_app.app_context():
        with flask_app.test_client() as client:
            user = UserModel.query.filter(UserModel.username == "test-user").scalar()
            response = client.get(f"/user/{user.id}")
            user_json = response.get_json()
            assert user_json["id"] == user.id
            assert user_json["username"] == user.username


def test_delete_user() -> None:
    flask_app = create_app()
    with flask_app.app_context():
        with flask_app.test_client() as client:
            user = UserModel.query.filter(UserModel.username == "test-user").scalar()
            response = client.delete(f"/user/{user.id}")
            resp_json = response.get_json()
            assert resp_json["message"] == "User deleted."
            assert response.status_code == HTTPStatus.OK
            assert UserModel.query.filter_by(id=user.id).first() == None
