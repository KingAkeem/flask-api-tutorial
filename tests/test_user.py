from app import create_app
from http import HTTPStatus


def test_register() -> None:
    flask_app = create_app()

    with flask_app.test_client() as client:
        test_json = {"username": "test-user", "password": "test-password"}
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
