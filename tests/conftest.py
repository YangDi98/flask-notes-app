import pytest
import os
from freezegun import freeze_time
from flask_migrate import upgrade
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
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": os.getenv(
            "TEST_DATABASE_URL", f"sqlite:///{TEST_DB_PATH}"
        ),
    }
    app = create_app(test_config)
    with app.app_context():
        upgrade()
        yield app


@pytest.fixture(autouse=True)
def clean_db(app):
    yield  # Run test first
    # Cleanup after each test
    with app.app_context():
        db.session.rollback()
        db.session.remove()

        # Clear all tables using a fresh connection
        with db.engine.connect() as connection:
            transaction = connection.begin()
            for table in reversed(db.metadata.sorted_tables):
                connection.execute(table.delete())
            transaction.commit()

        # Optional: dispose engine if you see pytest hang at the end
        db.engine.dispose()


@pytest.fixture
def db_session(app):
    """Returns a database session within app context."""
    with app.app_context():
        yield db


@pytest.fixture
def client(app):
    """Return a test client for making requests."""
    with app.test_client() as client:
        yield client


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


@pytest.fixture
def frozen_time_client(client, test_user):
    """Returns a function that creates authenticated client
    within frozen time."""

    def create_client_at_time(frozen_time):
        with freeze_time(frozen_time):
            response = client.post(
                "/auth/login",
                json={
                    "email": test_user.email,
                    "password": "password123@AAA",
                },
            )
            token = response.get_json()["access_token"]
            return AuthenticatedClient(client, token)

    return create_client_at_time
