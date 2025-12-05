from datetime import date

from app import (
    db,
    User,
    Horse,
    Competition,
    Result,
    ROLE_ADMIN,
    ROLE_JOCKEY,
    ROLE_OWNER,
)


def test_admin_can_create_result(client, app_ctx, admin_user, login):
    """
    Модули: /results/create + модели Competition/Horse/Result.

    Данные:
      - админ создаёт соревнование, лошадь, жокея;
      - затем добавляет результат.

    Ожидаемое:
      - запись в таблице results;
      - flash «Результат добавлен.»
    """
    # подготовка данных
    owner = User(username="owner_r", full_name="Owner R", role=ROLE_OWNER)
    owner.set_password("ownerpass")
    jockey = User(username="jockey_r", full_name="Жокей R", role=ROLE_JOCKEY, rating=4.5)
    jockey.set_password("jpass")

    db.session.add_all([owner, jockey])
    db.session.commit()

    horse = Horse(name="Ракета", sex="f", age=6, owner_id=owner.id)
    comp = Competition(
        name="Кубок Результатов",
        date=date(2025, 2, 1),
        time=None,
        place="Санкт-Петербург",
    )
    db.session.add_all([horse, comp])
    db.session.commit()

    login()  # логиним админа

    resp = client.post(
        "/results/create",
        data={
            "competition_id": str(comp.id),
            "horse_id": str(horse.id),
            "jockey_id": str(jockey.id),
            "place": "1",
            "race_time": "01:45.00",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "Результат добавлен." in text

    result = Result.query.filter_by(
        competition_id=comp.id,
        horse_id=horse.id,
        jockey_id=jockey.id,
    ).first()
    assert result is not None
    assert result.place == 1
    assert result.race_time == "01:45.00"


def test_admin_dashboard_shows_top_jockeys(client, app_ctx, admin_user, login):
    """
    Интеграционный тест: /dashboard для администратора.

    Модули:
      - dashboard (ROLE_ADMIN),
      - новая фича top_jockeys (топ-3 по rating).

    Ожидаемое:
      - на странице присутствуют имена трёх лучших жокеев;
      - жокей с более низким рейтингом (4-й) не попадает в топ.
    """
    # создаём админа уже через фикстуру admin_user
    # создаём 4-х жокеев с разным рейтингом
    j1 = User(username="j1", full_name="Жокей 1", role=ROLE_JOCKEY, rating=4.9)
    j1.set_password("j1pass")
    j2 = User(username="j2", full_name="Жокей 2", role=ROLE_JOCKEY, rating=4.5)
    j2.set_password("j2pass")
    j3 = User(username="j3", full_name="Жокей 3", role=ROLE_JOCKEY, rating=4.0)
    j3.set_password("j3pass")
    j4 = User(username="j4", full_name="Жокей 4", role=ROLE_JOCKEY, rating=3.0)
    j4.set_password("j4pass")

    db.session.add_all([j1, j2, j3, j4])
    db.session.commit()

    # логинимся под админом
    login()

    resp = client.get("/dashboard")
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)

    # ожидаем, что в HTML есть первые трое
    assert "Жокей 1" in text
    assert "Жокей 2" in text
    assert "Жокей 3" in text
    # а четвёртого (с низким рейтингом) нет
    assert "Жокей 4" not in text
