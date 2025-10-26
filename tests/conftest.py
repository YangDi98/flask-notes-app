import pytest
import os
from src import create_app
from src.extensions import db
from src.models.users import User

TEST_DB_PATH = "test_db.sqlite"


# Create a wrapper that adds Authorization header
class AuthenticatedClient:
    def __init__(self, client, token):
        self.client = client
        self.token = token

    def get(self, *args, **kwargs):
        kwargs.setdefault("headers", {})[
            "Authorization"
        ] = f"Bearer {self.token}"
        return self.client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs.setdefault("headers", {})[
            "Authorization"
        ] = f"Bearer {self.token}"
        return self.client.post(*args, **kwargs)

    def patch(self, *args, **kwargs):
        kwargs.setdefault("headers", {})[
            "Authorization"
        ] = f"Bearer {self.token}"
        return self.client.patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        kwargs.setdefault("headers", {})[
            "Authorization"
        ] = f"Bearer {self.token}"
        return self.client.put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault("headers", {})[
            "Authorization"
        ] = f"Bearer {self.token}"
        return self.client.delete(*args, **kwargs)


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{TEST_DB_PATH}",
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        # TEARDOWN PHASE (runs after all tests)
        db.drop_all()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(autouse=True)
def clean_db(app):
    yield  # Run test first
    # Cleanup after each test
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()


@pytest.fixture
def db_session(app):
    """Returns a database session within app context."""
    with app.app_context():
        yield db


@pytest.fixture
def client(app):
    """Return a test client for making requests."""
    return app.test_client()


@pytest.fixture
def test_user(db_session):
    user = User.create(
        data={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
        }
    )
    user.set_password("password123@AAA")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def authenticated_client(client, test_user, app):
    """Return a client already logged in as a test user."""

    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "password123@AAA"},
        follow_redirects=True,
    )
    token = response.get_json()["access_token"]
    return AuthenticatedClient(client, token)
