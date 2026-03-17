from http import HTTPStatus
from pytest import param
import pytest

from src.models.users import User


class TestUsers:
    @pytest.mark.parametrize(
        "update_data, expected_data",
        [
            param(
                {
                    "first_name": "UpdatedFirstName",
                    "last_name": "UpdatedLastName",
                    "preferred_language": "zh_CN",
                },
                {
                    "first_name": "UpdatedFirstName",
                    "last_name": "UpdatedLastName",
                    "preferred_language": "zh_CN",
                },
            ),
            param(
                {
                    "last_name": "UpdatedLastName",
                    "preferred_language": "zh_CN",
                },
                {
                    "first_name": "Test",
                    "last_name": "UpdatedLastName",
                    "preferred_language": "zh_CN",
                },
            ),
        ],
    )
    def test_update_user(
        self, test_user, authenticated_client, update_data, expected_data
    ):
        response = authenticated_client.patch(
            f"/api/users/{test_user.id}", json=update_data
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json["first_name"] == expected_data["first_name"]
        assert response.json["last_name"] == expected_data["last_name"]
        assert (
            response.json["preferred_language"]
            == expected_data["preferred_language"]
        )

    def test_update_user_unauthorized(self, test_user, client):
        update_data = {
            "first_name": "UpdatedFirstName",
            "last_name": "UpdatedLastName",
            "preferred_language": "zh_CN",
        }
        response = client.patch(f"/api/users/{test_user.id}", json=update_data)
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_update_user_forbidden(
        self, db_session, test_user, authenticated_client
    ):
        other_user = User.create(
            {
                "first_name": "other",
                "last_name": "user",
                "email": "other@example.com",
                "password": "password",
            }
        )
        db_session.session.commit()

        update_data = {
            "first_name": "UpdatedFirstName",
            "last_name": "UpdatedLastName",
            "preferred_language": "zh_CN",
        }
        response = authenticated_client.patch(
            f"/api/users/{other_user.id}", json=update_data
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_update_user_invalid_language(
        self, test_user, authenticated_client
    ):
        update_data = {
            "preferred_language": "unsupported_language",
        }
        response = authenticated_client.patch(
            f"/api/users/{test_user.id}", json=update_data
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json.get("message") == "Input Failed Validation"
