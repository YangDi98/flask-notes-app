from http import HTTPStatus


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

    def test_get_locale_with_accept_language(self, client, app):
        with app.app_context():
            # Test with Chinese Accept-Language header
            response = client.post(
                "/auth/register",
                json={
                    "first_name": "incomplete",
                    "password": "Validpass123@",
                },
                headers={"Accept-Language": "zh-CN"},
            )
            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert response.json.get("message") == "输入验证失败"
