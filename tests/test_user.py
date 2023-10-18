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
