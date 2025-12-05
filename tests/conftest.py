import os
import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app, db, User, ROLE_ADMIN, ROLE_JOCKEY, ROLE_OWNER  # noqa: E402


@pytest.fixture(scope="function")
def app_ctx():
    """Приложение во Flask-контексте с чистой тестовой БД."""
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL"),
        WTF_CSRF_ENABLED=False,
        LOGIN_DISABLED=False,
        SECRET_KEY="test-secret-key",
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app_ctx):
    """HTTP-клиент для интеграционных тестов."""
    return app_ctx.test_client()


@pytest.fixture()
def admin_user(app_ctx):
    """Администратор в тестовой базе."""
    admin = User(
        username="admin",
        full_name="Администратор",
        role=ROLE_ADMIN,
    )
    admin.set_password("adminpass")
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture()
def jockey_user(app_ctx):
    jockey = User(
        username="jockey1",
        full_name="Жокей Один",
        role=ROLE_JOCKEY,
        rating=4.5,
    )
    jockey.set_password("jockeypass")
    db.session.add(jockey)
    db.session.commit()
    return jockey


@pytest.fixture()
def owner_user(app_ctx):
    owner = User(
        username="owner1",
        full_name="Владелец Один",
        role=ROLE_OWNER,
        contact_info="owner@example.com",
    )
    owner.set_password("ownerpass")
    db.session.add(owner)
    db.session.commit()
    return owner
