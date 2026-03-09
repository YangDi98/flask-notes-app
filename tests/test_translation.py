from http import HTTPStatus
from pytest import param
import pytest


class TestTranslation:
    def test_get_locale_with_default_language(self, client, app):
        with app.app_context():
            response = client.post(
                "/auth/register",
                json={
                    "first_name": "incomplete",
                    "password": "Validpass123@",
                },
                # No Accept-Language header - should default to English
            )
            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert response.json.get("message") == "Input Failed Validation"

    @pytest.mark.parametrize(
        "accept_language, expected_message",
        [
            param("zh-CN", "输入验证失败"),
            param("en-US;q=0.8,zh-CN;q=0.9", "输入验证失败"),
            param("en-US", "Input Failed Validation"),
            param(
                "fr-FR", "Input Failed Validation"
            ),  # Unsupported language - should default to English
            param(
                "fr-FR,zh-CN;q=0.9", "输入验证失败"
            ),  # Unsupported primary language but supported secondary language
        ],
    )
    def test_get_locale_with_accept_language(
        self, client, app, accept_language, expected_message
    ):
        with app.app_context():
            # Test with Chinese Accept-Language header
            response = client.post(
                "/auth/register",
                json={
                    "first_name": "incomplete",
                    "password": "Validpass123@",
                },
                headers={"Accept-Language": accept_language},
            )
            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert response.json.get("message") == expected_message
