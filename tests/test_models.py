import pytest

from app import db, User, ROLE_JOCKEY


def test_user_password_hashing(app_ctx):
    """
    Модуль: модель User, методы set_password/check_password.

    Ожидаемое:
      - пароль хешируется;
      - check_password(True) на правильном пароле;
      - check_password(False) на неправильном.
    """
    user = User(username="test", full_name="Test User", role=ROLE_JOCKEY)
    user.set_password("secret")

    assert user.password_hash is not None
    assert user.check_password("secret")
    assert not user.check_password("wrong")


def test_register_creates_jockey_with_rating(client, app_ctx):
    """
    Модуль: обработчик /register.

    Данные:
      - форма регистрации с ролью 'jockey' и rating '4.2'.

    Ожидаемое:
      - создаётся пользователь с ролью 'jockey';
      - rating сохраняется как float 4.2.
    """
    response = client.post(
        "/register",
        data={
            "username": "testjockey",
            "full_name": "Тестовый Жокей",
            "password": "pass123",
            "role": "jockey",
            "age": "25",
            "rating": "4.2",
        },
        follow_redirects=True,
    )

    # после успешной регистрации происходит редирект на /login (status_code == 200 на целевой странице)
    assert response.status_code == 200

    user = User.query.filter_by(username="testjockey").first()
    assert user is not None
    assert user.role == ROLE_JOCKEY
    assert user.rating == pytest.approx(4.2)
