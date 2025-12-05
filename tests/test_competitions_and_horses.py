from datetime import date

from app import (
    db,
    User,
    Horse,
    Competition,
    ROLE_ADMIN,
    ROLE_JOCKEY,
    ROLE_OWNER,
)


def test_admin_can_create_competition(client, app_ctx, admin_user, login):
    """
    Модуль: /competitions/create.

    Данные:
      - админ создаёт состязание.

    Ожидаемое:
      - запись появляется в таблице competitions;
      - flash «Состязание добавлено.»
    """
    login()  # логиним админа

    resp = client.post(
        "/competitions/create",
        data={
            "name": "Кубок Теста",
            "date": "2025-01-01",
            "time": "12:30",
            "place": "Москва",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "Состязание добавлено." in text

    comp = Competition.query.filter_by(name="Кубок Теста").first()
    assert comp is not None
    assert comp.place == "Москва"
    assert comp.date == date(2025, 1, 1)


def test_owner_can_create_horse(client, app_ctx):
    """
    Модуль: /horses/create (роль owner).

    Ожидаемое:
      - создаётся лошадь, привязанная к владельцу;
      - flash «Лошадь добавлена.»
    """
    owner = User(username="owner_h", full_name="Owner Horse", role=ROLE_OWNER)
    owner.set_password("ownerpass")
    db.session.add(owner)
    db.session.commit()

    client.post(
        "/login",
        data={"username": "owner_h", "password": "ownerpass"},
        follow_redirects=True,
    )

    resp = client.post(
        "/horses/create",
        data={
            "name": "Буцефал",
            "sex": "m",
            "age": "5",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "Лошадь добавлена." in text

    horse = Horse.query.filter_by(name="Буцефал").first()
    assert horse is not None
    assert horse.owner_id == owner.id
    assert horse.age == 5


def test_jockey_cannot_create_horse(client, app_ctx):
    """
    Модуль: /horses/create (роль jockey).

    Ожидаемое:
      - доступ запрещён;
      - flash «Доступ запрещён.»
    """
    jockey = User(username="jockey_h", full_name="Jockey H", role=ROLE_JOCKEY)
    jockey.set_password("pass")
    db.session.add(jockey)
    db.session.commit()

    client.post(
        "/login",
        data={"username": "jockey_h", "password": "pass"},
        follow_redirects=True,
    )

    resp = client.post(
        "/horses/create",
        data={
            "name": "Чужая Лошадь",
            "sex": "f",
            "age": "4",
        },
        follow_redirects=True,
    )
    text = resp.get_data(as_text=True)
    assert "Доступ запрещён." in text
