from flask import Flask, session
import ast
from data.otziv import Otziv
from data import db_session
from data.users import User
from data.register import RegistrationForm
from data.login_form import LoginForm
from data.travel import Travel
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import render_template, redirect, abort, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/blogs.sqlite")


def main():
    @login_manager.user_loader
    def load_user(user_id):
        session = db_session.create_session()
        return session.query(User).get(user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            user = session.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)

    @app.route("/")
    def index():
        session = db_session.create_session()
        travel = session.query(Travel)
        return render_template("index.html", travel=travel)

    @app.route('/travel_form', methods=['GET', 'POST'])
    def travel_add():
        travel = Travel()
        session = db_session.create_session()
        if request.method == 'GET':
            return render_template('travel_form.html', title='Создание путешествия')
        elif request.method == 'POST':
            try:
                travel.headline = request.form['headline']
                travel.description = request.form['description']
                travel.creator = current_user.id
                img1 = request.files['img_1']
                img2 = request.files['img_2']
                img3 = request.files['img_3']
                travel.img_1 = img1.read()
                travel.img_2 = img2.read()
                travel.img_3 = img3.read()
                travel.route = request.form['route']
                session.add(travel)
                session.commit()
                return redirect('/')
            except Exception:
                return redirect('/travel_form')

    @app.route('/card', methods=['GET', 'POST'])
    def card():
        session = db_session.create_session()
        user = session.query(User).filter(User.id == current_user.id).first()
        f = open('static/img/avatar.jpg', 'wb')
        f.write(user.avatar)
        f.close()
        user.colvo_travel = len(list(session.query(Travel).filter(Travel.creator == current_user.id)))
        user.colvo_otziv = len(list(session.query(Otziv).filter(Otziv.creator_id == user.name)))
        session.commit()
        if request.method == 'GET':
            return render_template("card.html", user=user)
        elif request.method == 'POST':
            try:
                f = request.files['file']
                user.avatar = f.read()
                session.commit()
            except Exception:
                pass
            return redirect('/card')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            session = db_session.create_session()
            if session.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                email=form.email.data,
                surname=form.surname.data,
                age=form.age.data
            )
            user.set_password(form.password.data)
            session.add(user)
            session.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")

    @app.route("/travel/<int:id_travel>", methods=['GET', 'POST'])
    def travel(id_travel):
        session = db_session.create_session()
        travel = session.query(Travel).filter(Travel.id == id_travel).first()
        f = open('static/img/travel_1.jpg', 'wb')
        f.write(travel.img_1)
        f.close()
        f = open('static/img/travel_2.jpg', 'wb')
        f.write(travel.img_2)
        f.close()
        f = open('static/img/travel_3.jpg', 'wb')
        f.write(travel.img_3)
        f.close()
        if request.method == 'GET':
            otziv = session.query(Otziv).filter(Otziv.travel_id == id_travel)
            return render_template("travel.html", travel=travel, otziv=otziv)
        elif request.method == 'POST':
            otziv = Otziv()
            otziv.text = request.form['text']
            otziv.rating = int(request.form['rating'])
            otziv.creator_id = current_user.name
            otziv.travel_id = id_travel
            session.add(otziv)
            session.commit()
            return redirect(f'/travel/{id_travel}')

    @app.route('/travel_delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def travel_delete(id):
        session = db_session.create_session()
        travel = session.query(Travel).filter(Travel.id == id).first()
        if travel:
            session.delete(travel)
            otziv = session.query(Otziv).filter(Otziv.travel_id == travel.id)
            for i in otziv:
                session.delete(i)
            session.commit()
            current_user.colvo_travel = len(list(session.query(Travel).filter(Travel.creator == current_user.id)))
        else:
            abort(404)
        return redirect('/')

    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
