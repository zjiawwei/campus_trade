import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture
def app():
    """Create a Flask app with testing config and in-memory SQLite database."""
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """A Flask test client."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Access to the test database."""
    return _db


@pytest.fixture
def runner(app):
    """A Flask CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def logged_in_user(client, app):
    """Create a user and log them in. Returns the user id."""
    from app.services.user_service import create_user

    with app.app_context():
        user = create_user(
            username="testuser",
            student_id="20240001",
            email="test@campus.edu.cn",
            password="Test1234",
            campus="广州新港校区",
            real_name="测试用户",
        )

    client.post("/auth/login", data={
        "login_id": "testuser",
        "password": "Test1234",
    })

    return user.id
