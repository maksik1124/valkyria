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
