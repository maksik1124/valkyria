from datetime import date
from app import Competition, Horse, db


def login_as(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )

def test_admin_can_create_competition(client, admin_user, app_ctx):
    """
    Интеграционный тест: /competitions/create.

    Модуль: обработчик competition_create, декоратор admin_required.

    Данные: администратор добавляет новое состязание.

    Ожидаемый результат:
      - в БД появляется Competition с заданным именем и датой;
      - происходит редирект на список состязаний.
    """
    resp_login = login_as(client, "admin", "adminpass")
    assert resp_login.status_code == 200

    resp = client.post(
        "/competitions/create",
        data={
            "name": "Test Competition",
            "date": "2025-01-01",
            "time": "12:00",
            "place": "Test arena",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "Состязание добавлено" in text

    comp = Competition.query.filter_by(name="Test Competition").first()
    assert comp is not None
    assert comp.date == date(2025, 1, 1)

def test_non_admin_cannot_access_competition_create(client, jockey_user, app_ctx):
    """
    Интеграционный тест: защита админского маршрута.

    Модули: admin_required, /competitions/create.

    Данные: авторизованный жокей.

    Ожидаемый результат:
      - доступ запрещён, редирект на index, флеш 'Требуются права администратора'.
    """
    resp_login = login_as(client, "jockey1", "jockeypass")
    assert resp_login.status_code == 200

    resp = client.get("/competitions/create", follow_redirects=True)
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "Требуются права администратора" in text


from app import User, ROLE_OWNER


def test_owner_sees_only_own_horses(client, owner_user, app_ctx):
    """
    Интеграционный тест: /horses для владельца.

    Модули: horses_list, horse_create.

    Данные:
      - лошади двух владельцев.

    Ожидаемый результат:
      - в ответе только лошади текущего владельца.
    """
    # второй владелец
    owner2 = User(
        username="owner2", full_name="Владелец Два", role=ROLE_OWNER
    )
    owner2.set_password("owner2pass")
    db.session.add(owner2)
    db.session.commit()

    horse1 = Horse(name="Horse1", sex="m", age=5, owner_id=owner_user.id)
    horse2 = Horse(name="Horse2", sex="f", age=7, owner_id=owner2.id)
    db.session.add_all([horse1, horse2])
    db.session.commit()

    resp_login = login_as(client, "owner1", "ownerpass")
    assert resp_login.status_code == 200

    resp = client.get("/horses")
    assert resp.status_code == 200
    data = resp.data.decode("utf-8")
    assert "Horse1" in data
    assert "Horse2" not in data
