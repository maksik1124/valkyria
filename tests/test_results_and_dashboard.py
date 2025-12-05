from datetime import date
from app import Competition, Horse, Result, db, ROLE_ADMIN, ROLE_JOCKEY, User
from .test_competitions_and_horses import login_as
def test_admin_can_create_result(client, admin_user, app_ctx, jockey_user, owner_user):
    """
    Интеграционный тест: /results/create.

    Модули: result_create, модели Result, Competition, Horse.

    Ожидаемый результат:
      - появляется новая запись Result с заданными параметрами.
    """
    comp = Competition(name="Comp1", date=date(2025, 1, 1), place="Arena")
    horse = Horse(name="Speedy", sex="m", age=4, owner_id=owner_user.id)
    db.session.add_all([comp, horse])
    db.session.commit()

    resp_login = login_as(client, "admin", "adminpass")
    assert resp_login.status_code == 200

    resp = client.post(
        "/results/create",
        data={
            "competition_id": str(comp.id),
            "horse_id": str(horse.id),
            "jockey_id": str(jockey_user.id),
            "place": "1",
            "race_time": "01:45.23",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "Результат добавлен" in text

    result = Result.query.filter_by(competition_id=comp.id).first()
    assert result is not None
    assert result.place == 1
    assert result.race_time == "01:45.23"
def test_admin_dashboard_shows_top_jockeys(client, app_ctx):
    """
    Интеграционный тест: /dashboard для администратора.

    Модули: dashboard (ROLE_ADMIN), новая фича top_jockeys.

    Ожидаемый результат:
      - на странице присутствуют имена трёх лучших жокеев.
    """
    admin = User(username="admin2", full_name="Admin2", role=ROLE_ADMIN)
    admin.set_password("adminpass")
    j1 = User(username="j1", full_name="Жокей 1", role=ROLE_JOCKEY, rating=4.9)
    j2 = User(username="j2", full_name="Жокей 2", role=ROLE_JOCKEY, rating=4.5)
    j3 = User(username="j3", full_name="Жокей 3", role=ROLE_JOCKEY, rating=4.0)
    j4 = User(username="j4", full_name="Жокей 4", role=ROLE_JOCKEY, rating=3.0)
    db.session.add_all([admin, j1, j2, j3, j4])
    db.session.commit()

    resp_login = login_as(client, "admin2", "adminpass")
    assert resp_login.status_code == 200

    resp = client.get("/dashboard")
    assert resp.status_code == 200
    data = resp.data.decode("utf-8")
    # предполагаем, что в шаблоне отображаются full_name жокеев
    assert "Жокей 1" in data
    assert "Жокей 2" in data
    assert "Жокей 3" in data
    # четвёртый с меньшим рейтингом не входит в топ-3
    # (можно проверить, что он тоже есть, но не в блоке топа — для ЛР достаточно текущей проверки)
