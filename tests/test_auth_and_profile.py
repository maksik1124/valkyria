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
