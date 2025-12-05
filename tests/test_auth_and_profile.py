import pytest
from app import User


def test_login_success_redirects_to_dashboard(client, app_ctx):
    """
    Интеграционный тест: /login.

    Модули: модель User, обработчик /login, Flask-Login.

    Данные:
      - существующий пользователь с корректным паролем.

    Ожидаемый результат:
      - POST /login -> редирект (302) на /dashboard;
      - флеш 'Успешный вход в систему.' присутствует в ответе.
    """
    user = User(username="authuser", full_name="Auth User", role="jockey")
    user.set_password("mypassword")
    from app import db

    db.session.add(user)
    db.session.commit()

    resp = client.post(
        "/login",
        data={"username": "authuser", "password": "mypassword"},
        follow_redirects=True,
    )

    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "Успешный вход в систему" in text


def test_login_wrong_password_shows_error(client, app_ctx):
    """
    Интеграционный тест: /login с неверным паролем.

    Ожидаемый результат: остаёмся на странице логина, сообщение об ошибке.
    """
    user = User(username="authuser2", full_name="Auth User 2", role="jockey")
    user.set_password("correct")
    from app import db

    db.session.add(user)
    db.session.commit()

    resp = client.post(
        "/login",
        data={"username": "authuser2", "password": "wrong"},
        follow_redirects=True,
    )

    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "Неверный логин или пароль" in text

def test_profile_update_changes_age_and_contact(client, owner_user, app_ctx):
    """
    Интеграционный тест: /profile (GET+POST).

    Модуль: обработчик /profile.

    Данные: владелец обновляет возраст и контакты.

    Ожидаемый результат:
      - в БД обновляется age и contact_info;
      - флеш 'Профиль обновлён.' в ответе.
    """
    # Логинимся как owner_user
    resp_login = client.post(
        "/login",
        data={"username": "owner1", "password": "ownerpass"},
        follow_redirects=True,
    )
    assert resp_login.status_code == 200

    resp = client.post(
        "/profile",
        data={
            "full_name": "Владелец Один",
            "age": "30",
            "address": "Some street",
            "contact_info": "newemail@example.com",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "Профиль обновлён" in text

    from app import db

    db.session.refresh(owner_user)
    assert owner_user.age == 30
    assert owner_user.contact_info == "newemail@example.com"
import pytest

from app import db, User, ROLE_JOCKEY, ROLE_OWNER


def test_register_and_login_owner(client, app_ctx):
    """
    Модули: /register, /login.

    Данные:
      - регистрация владельца, затем попытка входа.

    Ожидаемое:
      - успешная регистрация (flash-сообщение);
      - успешный вход (flash «Успешный вход в систему.»).
    """
    resp = client.post(
        "/register",
        data={
            "username": "owner1",
            "full_name": "Владелец 1",
            "password": "ownerpass",
            "role": "owner",
            "age": "40",
            "contact_info": "owner@example.com",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "Регистрация прошла успешно" in text

    resp2 = client.post(
        "/login",
        data={"username": "owner1", "password": "ownerpass"},
        follow_redirects=True,
    )
    assert resp2.status_code == 200
    assert "Успешный вход в систему." in resp2.get_data(as_text=True)


def test_login_wrong_password_shows_error(client, app_ctx):
    """
    Модуль: /login.

    Данные:
      - существующий пользователь;
      - неправильный пароль.

    Ожидаемое:
      - flash «Неверный логин или пароль.»
    """
    user = User(username="user1", full_name="User 1", role=ROLE_JOCKEY)
    user.set_password("correct")
    db.session.add(user)
    db.session.commit()

    resp = client.post(
        "/login",
        data={"username": "user1", "password": "wrong"},
        follow_redirects=True,
    )

    text = resp.get_data(as_text=True)
    assert "Неверный логин или пароль." in text


def test_profile_update_jockey_rating(client, app_ctx):
    """
    Модуль: /profile (POST) для жокея.

    Данные:
      - изменение ФИО и rating.

    Ожидаемое:
      - в БД обновлены full_name и rating;
      - flash «Профиль обновлён.»
    """
    jockey = User(username="jockey1", full_name="Старое имя", role=ROLE_JOCKEY)
    jockey.set_password("pass")
    db.session.add(jockey)
    db.session.commit()

    # логинимся
    resp_login = client.post(
        "/login",
        data={"username": "jockey1", "password": "pass"},
        follow_redirects=True,
    )
    assert resp_login.status_code == 200

    resp = client.post(
        "/profile",
        data={
            "full_name": "Новое Имя",
            "age": "26",
            "address": " Нью-адрес",
            "rating": "4.8",
            "contact_info": "",
        },
        follow_redirects=True,
    )
    text = resp.get_data(as_text=True)
    assert "Профиль обновлён." in text

    db.session.refresh(jockey)
    assert jockey.full_name == "Новое Имя"
    assert jockey.age == 26
    assert jockey.rating == pytest.approx(4.8)


def test_profile_invalid_age_shows_error(client, app_ctx):
    """
    Модуль: /profile (POST).

    Данные:
      - age='abc'.

    Ожидаемое:
      - flash «Возраст должен быть числом.»
    """
    user = User(username="user2", full_name="User 2", role=ROLE_OWNER)
    user.set_password("pass")
    db.session.add(user)
    db.session.commit()

    client.post(
        "/login",
        data={"username": "user2", "password": "pass"},
        follow_redirects=True,
    )

    resp = client.post(
        "/profile",
        data={"full_name": "User 2", "age": "abc"},
        follow_redirects=True,
    )
    text = resp.get_data(as_text=True)
    assert "Возраст должен быть числом." in text
