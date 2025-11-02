from sqlalchemy import select
from http import HTTPStatus
from src.models.users import User


class TestAuth:
    def test_register_new_user(self, client, app, db_session):
        response = client.post(
            "/auth/register",
            json={
                "first_name": "newuser",
                "last_name": "tester",
                "email": "new@example.com",
                "password": "mypassword123@AAA",
            },
        )
        assert response.status_code == HTTPStatus.CREATED
        user = db_session.session.execute(
            select(User).where(
                User.first_name == "newuser", User.last_name == "tester"
            )
        ).scalar_one_or_none()
        assert user is not None
        assert user.email == "new@example.com"

    def test_register_existing_email(self, client, app, db_session):
        # First, create a user
        existing_user = User.create(
            {
                "first_name": "existing",
                "last_name": "user",
                "email": "existing@example.com",
                "password": "mypassword123@AAA",
            }
        )
        assert existing_user is not None

        # Now, try to register a new user with the same email
        response = client.post(
            "/auth/register",
            json={
                "first_name": "newuser",
                "last_name": "tester",
                "email": "existing@example.com",
                "password": "mypassword123@AAA",
            },
        )
        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json.get("message") == "Email already registered"

    def test_register_invalid_password(self, client, app):
        response = client.post(
            "/auth/register",
            json={
                "first_name": "weakpassword",
                "last_name": "tester",
                "email": "weakpassword@example.com",
                "password": "weak",
            },
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json.get("message") == "Input Failed Validation"
        assert response.json.get("details").get("json").get("_schema") == [
            "Invalid Password"
        ]

    def test_register_invalid_email(self, client, app):
        response = client.post(
            "/auth/register",
            json={
                "first_name": "invalidemail",
                "last_name": "tester",
                "email": "not-an-email",
                "password": "Validpass123@",
            },
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json.get("message") == "Input Failed Validation"
        assert response.json.get("details").get("json").get("_schema") == [
            "Invalid Email Address"
        ]

    def test_register_missing_fields(self, client, app):
        response = client.post(
            "/auth/register",
            json={
                "first_name": "incomplete",
                # Missing last_name and email
                "password": "Validpass123@",
            },
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json.get("message") == "Input Failed Validation"

    def test_register_user_uppercase_email(self, client, app, db_session):
        response = client.post(
            "/auth/register",
            json={
                "first_name": "uppercaseemail",
                "last_name": "tester",
                "email": "UPPERCASEEMAIL@EXAMPLE.COM",
                "password": "Validpass123@",
            },
        )
        assert response.status_code == HTTPStatus.CREATED
        assert response.json.get("email") == "uppercaseemail@example.com"

    def test_login_valid_user(self, client, app, test_user):
        response = client.post(
            "/auth/login",
            json={"email": test_user.email, "password": "password123@AAA"},
        )
        assert response.status_code == HTTPStatus.OK
        assert "access_token" in response.get_json()
        # Check if refresh token cookie is set
        cookies = response.headers.getlist("Set-Cookie")
        refresh_cookie_found = any(
            "refresh_token=" in cookie for cookie in cookies
        )
        assert refresh_cookie_found, "Refresh token cookie should be set"

    def test_login_valid_user_uppercase_email(self, client, app, test_user):
        response = client.post(
            "/auth/login",
            json={
                "email": test_user.email.upper(),
                "password": "password123@AAA",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert "access_token" in response.get_json()
        # Check if refresh token cookie is set
        cookies = response.headers.getlist("Set-Cookie")
        refresh_cookie_found = any(
            "refresh_token=" in cookie for cookie in cookies
        )
        assert refresh_cookie_found, "Refresh token cookie should be set"

    def test_login_invalid_password(self, client, app, test_user):
        response = client.post(
            "/auth/login",
            json={"email": test_user.email, "password": "wrongpassword"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json.get("message") == "Invalid email or password"

    def test_login_invalid_email(self, client, app):
        response = client.post(
            "/auth/login",
            json={"email": "invalid@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json.get("message") == "Invalid email or password"

    def test_login_inactive_user(self, client, app, db_session):
        inactive_user = User.create(
            {
                "first_name": "inactive",
                "last_name": "user",
                "email": "inactive@example.com",
            }
        )
        inactive_user.update({"active": False}, commit=True)
        inactive_user.set_password("Somepass123@A")
        response = client.post(
            "/auth/login",
            json={"email": inactive_user.email, "password": "Somepass123@A"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json.get("message") == "Invalid email or password"

    def test_login_deleted_user(self, client, app, db_session):
        deleted_user = User.create(
            {
                "first_name": "deleted",
                "last_name": "user",
                "email": "deleted@example.com",
            }
        )
        deleted_user.set_password("Somepass123@A")
        deleted_user.soft_delete(commit=True)
        response = client.post(
            "/auth/login",
            json={"email": deleted_user.email, "password": "Somepass123@A"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json.get("message") == "Invalid email or password"

    def test_logout_user(self, test_user, authenticated_client):
        response = authenticated_client.post("/auth/logout")
        assert response.status_code == HTTPStatus.OK
        assert response.json.get("message") == "logout successful"
        assert test_user.last_logout_at is not None

    def test_protected_route_after_logout(
        self, test_user, authenticated_client
    ):
        # First logout
        response = authenticated_client.post("/auth/logout")
        assert response.status_code == HTTPStatus.OK

        # Now try to access protected route
        response = authenticated_client.get("/auth/protected")
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json.get("message") == "Token has been revoked."

    def test_protected_route_with_authenticated_user(
        self, test_user, authenticated_client
    ):
        response = authenticated_client.get(f"/users/{test_user.id}/notes/")
        assert response.status_code == 200
