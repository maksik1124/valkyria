import os
import sys
from pathlib import Path

import pytest

# Путь к корню проекта = родительская папка относительно tests/
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Для тестов используем SQLite в памяти, а не реальную PostgreSQL
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

import os
import sys
from pathlib import Path

import pytest

# ВАЖНО: подменяем БД на SQLite ДО импорта app.py
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import (  # noqa: E402
    app,
    db,
    User,
    Horse,
    Competition,
    Result,
    ROLE_ADMIN,
    ROLE_JOCKEY,
    ROLE_OWNER,
)


@pytest.fixture
def app_ctx():
    """
    Чистый app context и чистая БД для каждого теста.
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app_ctx):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def admin_user(app_ctx):
    """Админ для тестов."""
    admin = User(
        username="admin",
        full_name="Администратор",
        role=ROLE_ADMIN,
    )
    admin.set_password("adminpass")
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def login(client, admin_user):
    """
    Фикстура-хелпер: login() логинит админа по умолчанию,
    либо любого другого пользователя по логину/паролю.
    """

    def _login(username="admin", password="adminpass"):
        return client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    return _login
