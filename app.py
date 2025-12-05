import os
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
    UserMixin,
)
from werkzeug.security import generate_password_hash, check_password_hash

# Инициализация приложения
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

# Пример строки подключения (переопределяется переменной окружения DATABASE_URL)
default_db_url = "postgresql+psycopg2://valkyria_user:valkyria_password@localhost/valkyria_db"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", default_db_url)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

ROLE_ADMIN = "admin"
ROLE_JOCKEY = "jockey"
ROLE_OWNER = "owner"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    full_name = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer)
    address = db.Column(db.String(255))
    rating = db.Column(db.Float)  # рейтинг жокея
    contact_info = db.Column(db.String(255))  # контакты владельца

    horses = db.relationship("Horse", backref="owner", lazy=True)
    jockey_results = db.relationship(
        "Result",
        backref="jockey",
        foreign_keys="Result.jockey_id",
        lazy=True,
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Horse(db.Model):
    __tablename__ = "horses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    sex = db.Column(db.String(10))
    age = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    results = db.relationship("Result", backref="horse", lazy=True)


class Competition(db.Model):
    __tablename__ = "competitions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=True)
    place = db.Column(db.String(128))

    results = db.relationship("Result", backref="competition", lazy=True)


class Result(db.Model):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(
        db.Integer, db.ForeignKey("competitions.id"), nullable=False
    )
    horse_id = db.Column(db.Integer, db.ForeignKey("horses.id"), nullable=False)
    jockey_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    place = db.Column(db.Integer)
    race_time = db.Column(
        db.String(32)
    )  # строка вида "01:45.23" (минуты:секунды.доли)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    """Декоратор для проверки прав администратора."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != ROLE_ADMIN:
            flash("Требуются права администратора", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    """Общедоступная информация о состязаниях и результатах."""
    competitions = (
        Competition.query.order_by(Competition.date.desc(), Competition.time.desc())
        .all()
    )
    return render_template("index.html", competitions=competitions)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role")

        age_raw = request.form.get("age")
        address = request.form.get("address")
        rating_raw = request.form.get("rating")
        contact_info = request.form.get("contact_info")

        if role not in (ROLE_JOCKEY, ROLE_OWNER):
            flash("Регистрация доступна только для ролей жокея и владельца.", "danger")
            return redirect(url_for("register"))

        if not username or not full_name or not password:
            flash("Заполните обязательные поля.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Пользователь с таким логином уже существует.", "danger")
            return redirect(url_for("register"))

        try:
            age = int(age_raw) if age_raw else None
        except ValueError:
            age = None

        try:
            rating = float(rating_raw) if rating_raw else None
        except ValueError:
            rating = None

        user = User(
            username=username,
            full_name=full_name,
            role=role,
            age=age,
            address=address,
            rating=rating if role == ROLE_JOCKEY else None,
            contact_info=contact_info if role == ROLE_OWNER else None,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Регистрация прошла успешно. Теперь войдите в систему.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Успешный вход в систему.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        else:
            flash("Неверный логин или пароль.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.", "success")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    """Личный кабинет пользователя в зависимости от роли."""
    if current_user.role == ROLE_ADMIN:
        competitions_count = Competition.query.count()
        horses_count = Horse.query.count()
        results_count = Result.query.count()

        # Топ-3 жокея по рейтингу
        top_jockeys = (
            User.query.filter_by(role=ROLE_JOCKEY)
            .filter(User.rating.isnot(None))
            .order_by(User.rating.desc())
            .limit(3)
            .all()
        )

        return render_template(
            "dashboard.html",
            competitions_count=competitions_count,
            horses_count=horses_count,
            results_count=results_count,
            top_jockeys=top_jockeys,
        )

    elif current_user.role == ROLE_JOCKEY:
        results = (
            Result.query.filter_by(jockey_id=current_user.id)
            .join(Competition)
            .order_by(Competition.date.desc())
            .all()
        )
        return render_template("dashboard.html", results=results)

    elif current_user.role == ROLE_OWNER:
        horses = Horse.query.filter_by(owner_id=current_user.id).all()
        results = (
            Result.query.join(Horse)
            .filter(Horse.owner_id == current_user.id)
            .join(Competition)
            .order_by(Competition.date.desc())
            .all()
        )
        return render_template("dashboard.html", horses=horses, results=results)

    else:
        flash("Неизвестная роль пользователя.", "danger")
        return redirect(url_for("index"))



@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user

    if request.method == "POST":
        user.full_name = request.form.get("full_name", user.full_name)
        age_raw = request.form.get("age")
        user.address = request.form.get("address")
        user.contact_info = request.form.get("contact_info")

        if age_raw:
            try:
                user.age = int(age_raw)
            except ValueError:
                flash("Возраст должен быть числом.", "danger")

        if user.role == ROLE_JOCKEY:
            rating_raw = request.form.get("rating")
            if rating_raw:
                try:
                    user.rating = float(rating_raw)
                except ValueError:
                    flash("Рейтинг должен быть числом.", "danger")

        db.session.commit()
        flash("Профиль обновлён.", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


@app.route("/competitions")
def competitions_list():
    competitions = (
        Competition.query.order_by(Competition.date.desc(), Competition.time.desc())
        .all()
    )
    return render_template("competitions.html", competitions=competitions)


@app.route("/competitions/create", methods=["GET", "POST"])
@login_required
@admin_required
def competition_create():
    if request.method == "POST":
        name = request.form.get("name")
        date_str = request.form.get("date")
        time_str = request.form.get("time")
        place = request.form.get("place")

        if not name or not date_str:
            flash("Название и дата обязательны.", "danger")
            return redirect(url_for("competition_create"))

        try:
            comp_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Некорректный формат даты.", "danger")
            return redirect(url_for("competition_create"))

        comp_time = None
        if time_str:
            try:
                comp_time = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                flash("Некорректный формат времени.", "danger")
                return redirect(url_for("competition_create"))

        competition = Competition(name=name, date=comp_date, time=comp_time, place=place)
        db.session.add(competition)
        db.session.commit()
        flash("Состязание добавлено.", "success")
        return redirect(url_for("competitions_list"))

    return render_template("competition_form.html", competition=None)


@app.route("/competitions/<int:competition_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def competition_edit(competition_id):
    competition = Competition.query.get_or_404(competition_id)
    if request.method == "POST":
        name = request.form.get("name")
        date_str = request.form.get("date")
        time_str = request.form.get("time")
        place = request.form.get("place")

        if not name or not date_str:
            flash("Название и дата обязательны.", "danger")
            return redirect(url_for("competition_edit", competition_id=competition.id))

        try:
            competition.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Некорректный формат даты.", "danger")
            return redirect(url_for("competition_edit", competition_id=competition.id))

        if time_str:
            try:
                competition.time = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                flash("Некорректный формат времени.", "danger")
                return redirect(url_for("competition_edit", competition_id=competition.id))

        competition.name = name
        competition.place = place

        db.session.commit()
        flash("Состязание обновлено.", "success")
        return redirect(url_for("competitions_list"))

    return render_template("competition_form.html", competition=competition)


@app.route("/competitions/<int:competition_id>/delete", methods=["POST"])
@login_required
@admin_required
def competition_delete(competition_id):
    competition = Competition.query.get_or_404(competition_id)
    db.session.delete(competition)
    db.session.commit()
    flash("Состязание удалено.", "success")
    return redirect(url_for("competitions_list"))


@app.route("/horses")
@login_required
def horses_list():
    if current_user.role == ROLE_ADMIN:
        horses = Horse.query.all()
    else:
        horses = Horse.query.filter_by(owner_id=current_user.id).all()
    return render_template("horses.html", horses=horses)


@app.route("/horses/create", methods=["GET", "POST"])
@login_required
def horse_create():
    if current_user.role not in (ROLE_ADMIN, ROLE_OWNER):
        flash("Доступ запрещён.", "danger")
        return redirect(url_for("horses_list"))

    if request.method == "POST":
        name = request.form.get("name")
        sex = request.form.get("sex")
        age_raw = request.form.get("age")

        if not name:
            flash("Кличка лошади обязательна.", "danger")
            return redirect(url_for("horse_create"))

        try:
            age = int(age_raw) if age_raw else None
        except ValueError:
            age = None

        owner_id = current_user.id
        if current_user.role == ROLE_ADMIN:
            # администратор может выбрать владельца
            owner_id_raw = request.form.get("owner_id")
            if owner_id_raw:
                try:
                    owner_id = int(owner_id_raw)
                except ValueError:
                    pass

        horse = Horse(name=name, sex=sex, age=age, owner_id=owner_id)
        db.session.add(horse)
        db.session.commit()
        flash("Лошадь добавлена.", "success")
        return redirect(url_for("horses_list"))

    owners = []
    if current_user.role == ROLE_ADMIN:
        owners = User.query.filter_by(role=ROLE_OWNER).all()

    return render_template("horse_form.html", horse=None, owners=owners)


@app.route("/horses/<int:horse_id>/edit", methods=["GET", "POST"])
@login_required
def horse_edit(horse_id):
    horse = Horse.query.get_or_404(horse_id)

    if current_user.role == ROLE_OWNER and horse.owner_id != current_user.id:
        flash("Вы можете редактировать только своих лошадей.", "danger")
        return redirect(url_for("horses_list"))

    if current_user.role not in (ROLE_ADMIN, ROLE_OWNER):
        flash("Доступ запрещён.", "danger")
        return redirect(url_for("horses_list"))

    if request.method == "POST":
        name = request.form.get("name")
        sex = request.form.get("sex")
        age_raw = request.form.get("age")

        if not name:
            flash("Кличка лошади обязательна.", "danger")
            return redirect(url_for("horse_edit", horse_id=horse.id))

        try:
            horse.age = int(age_raw) if age_raw else None
        except ValueError:
            pass

        horse.name = name
        horse.sex = sex

        if current_user.role == ROLE_ADMIN:
            owner_id_raw = request.form.get("owner_id")
            if owner_id_raw:
                try:
                    horse.owner_id = int(owner_id_raw)
                except ValueError:
                    pass

        db.session.commit()
        flash("Данные лошади обновлены.", "success")
        return redirect(url_for("horses_list"))

    owners = []
    if current_user.role == ROLE_ADMIN:
        owners = User.query.filter_by(role=ROLE_OWNER).all()

    return render_template("horse_form.html", horse=horse, owners=owners)


@app.route("/horses/<int:horse_id>/delete", methods=["POST"])
@login_required
def horse_delete(horse_id):
    horse = Horse.query.get_or_404(horse_id)

    if current_user.role == ROLE_OWNER and horse.owner_id != current_user.id:
        flash("Вы можете удалять только своих лошадей.", "danger")
        return redirect(url_for("horses_list"))

    if current_user.role not in (ROLE_ADMIN, ROLE_OWNER):
        flash("Доступ запрещён.", "danger")
        return redirect(url_for("horses_list"))

    db.session.delete(horse)
    db.session.commit()
    flash("Лошадь удалена.", "success")
    return redirect(url_for("horses_list"))


@app.route("/results")
def results_list():
    results = (
        Result.query.join(Competition)
        .order_by(Competition.date.desc(), Result.place.asc())
        .all()
    )
    return render_template("results.html", results=results)


@app.route("/results/create", methods=["GET", "POST"])
@login_required
@admin_required
def result_create():
    competitions = Competition.query.order_by(Competition.date.desc()).all()
    horses = Horse.query.all()
    jockeys = User.query.filter_by(role=ROLE_JOCKEY).all()

    if request.method == "POST":
        competition_id = request.form.get("competition_id")
        horse_id = request.form.get("horse_id")
        jockey_id = request.form.get("jockey_id")
        place_raw = request.form.get("place")
        race_time = request.form.get("race_time")

        if not (competition_id and horse_id and jockey_id):
            flash("Заполните все обязательные поля.", "danger")
            return redirect(url_for("result_create"))

        try:
            place = int(place_raw) if place_raw else None
        except ValueError:
            place = None

        result = Result(
            competition_id=int(competition_id),
            horse_id=int(horse_id),
            jockey_id=int(jockey_id),
            place=place,
            race_time=race_time,
        )
        db.session.add(result)
        db.session.commit()
        flash("Результат добавлен.", "success")
        return redirect(url_for("results_list"))

    return render_template(
        "result_form.html",
        result=None,
        competitions=competitions,
        horses=horses,
        jockeys=jockeys,
    )


@app.route("/results/<int:result_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def result_edit(result_id):
    result = Result.query.get_or_404(result_id)
    competitions = Competition.query.order_by(Competition.date.desc()).all()
    horses = Horse.query.all()
    jockeys = User.query.filter_by(role=ROLE_JOCKEY).all()

    if request.method == "POST":
        competition_id = request.form.get("competition_id")
        horse_id = request.form.get("horse_id")
        jockey_id = request.form.get("jockey_id")
        place_raw = request.form.get("place")
        race_time = request.form.get("race_time")

        if not (competition_id and horse_id and jockey_id):
            flash("Заполните все обязательные поля.", "danger")
            return redirect(url_for("result_edit", result_id=result.id))

        try:
            result.place = int(place_raw) if place_raw else None
        except ValueError:
            pass

        result.competition_id = int(competition_id)
        result.horse_id = int(horse_id)
        result.jockey_id = int(jockey_id)
        result.race_time = race_time

        db.session.commit()
        flash("Результат обновлён.", "success")
        return redirect(url_for("results_list"))

    return render_template(
        "result_form.html",
        result=result,
        competitions=competitions,
        horses=horses,
        jockeys=jockeys,
    )


@app.route("/results/<int:result_id>/delete", methods=["POST"])
@login_required
@admin_required
def result_delete(result_id):
    result = Result.query.get_or_404(result_id)
    db.session.delete(result)
    db.session.commit()
    flash("Результат удалён.", "success")
    return redirect(url_for("results_list"))


@app.cli.command("init-db")
def init_db():
    """Создание таблиц в базе данных."""
    db.create_all()
    print("База данных инициализирована.")


@app.cli.command("create-admin")
def create_admin():
    """Интерактивное создание администратора."""
    import getpass

    username = input("Логин администратора: ").strip()
    full_name = input("ФИО администратора: ").strip()
    password = getpass.getpass("Пароль: ")

    if not username or not full_name or not password:
        print("Все поля обязательны.")
        return

    if User.query.filter_by(username=username).first():
        print("Пользователь с таким логином уже существует.")
        return

    user = User(username=username, full_name=full_name, role=ROLE_ADMIN)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print("Администратор создан.")


if __name__ == "__main__":
    # Локальный запуск для разработки
    app.run(debug=False)
