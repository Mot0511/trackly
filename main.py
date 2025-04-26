from flask import Flask, render_template, redirect, abort, request
from db.db_session import global_init, create_session
from flask_login import LoginManager, login_user, login_required, logout_user
import flask_login
from db.models import User, Site
from forms.login import LoginForm
from forms.register import RegisterForm
from forms.site import SiteForm
from forms.upload_icon_form import UploadIconForm
import datetime
from utils.load_processes import load_processes
from utils.worker import worker
from multiprocessing import Process
import os
from scheduler import scheduler
from api import api_router
import time
from sys import platform

app = Flask(__name__)
app.register_blueprint(api_router)

login_manager = LoginManager()
login_manager.init_app(app)

global_init('db/db.db')
    
load_processes(scheduler)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

jobs = {}

@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.query(User).get(user_id)

@app.post('/editSite/<id>')
@login_required
def editSite(id):
    form = SiteForm()

    if form.validate_on_submit():
        user = flask_login.current_user
        session = create_session()
        site = session.query(Site).filter(Site.id == id, Site.user == user).first()
        site.name = form.name.data
        site.url = form.url.data
        session.commit()

        if request.files['icon']:
            with open(f'userdata/icons/{site.id}.png', 'wb') as f:
                f.write(request.files['icon'].read())

        return redirect('/')

@app.get('/removeSite/<id>')
@login_required
def removeSite(id):
    user = flask_login.current_user
    session = create_session()

    site = session.query(Site).filter(Site.id == id, Site.user == user).first()

    if not site: abort(404)

    session.delete(site)
    session.commit()

    if os.path.exists(f'userdata/icons/{site.id}.png'):
        os.remove(f'userdata/icons/{site.id}.png')

    scheduler.remove_job(str(site.id))

    return redirect('/')


@app.route('/', methods=["GET", "POST"])
def sites():
    user = flask_login.current_user
    if not user.is_authenticated: return redirect('/signin')

    form = SiteForm()
    upload_icon_form = UploadIconForm()
    if form.validate_on_submit():
        session = create_session()
        if session.query(Site).filter(Site.url == form.url.data).first():
            return render_template('sites.html', title='Мои сайты', message='Такой сайт уже добавлен', form=form)

        id = datetime.datetime.now().timestamp()
        site = Site(
            id = int(id),
            name = form.name.data,
            url = form.url.data,
        )
        user.sites.append(site)
        session.merge(user)
        session.commit()

        scheduler.add_job(lambda: worker(site), 'interval', seconds=5, id=str(site.id))

        if request.files['icon']:
            with open(f'userdata/icons/{site.id}.png', 'wb') as f:
                f.write(request.files['icon'].read())

    return render_template('sites.html', title='Мои сайты', form=form, upload_icon_form=upload_icon_form)

@app.get('/about')
def about():
    return render_template('about.html', title='О сервисе')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        session = create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect('/')
        return render_template('signin.html',message="Неправильный логин или пароль",form=form)

    return render_template('signin.html', title='Вход', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        if not form.password.data == form.repeat_password.data:
            return render_template('signup.html', title='Регистрация', form=form, message='Пароли не совпадают')

        session = create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('signup.html', title='Регистрация', form=form, message='Такой пользователь уже существует')

        user = User(
            email = form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        login_user(user, remember=True)
        return redirect('/')

    return render_template('signup.html', title='Регистрация', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/signin')


def main():
    app.run(port=3000)

if __name__ == '__main__':
    main()