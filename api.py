from flask import Blueprint, jsonify, abort, render_template, request, send_file, make_response
from flask_login import login_required
import flask_login
from db.db_session import create_session
from db.models import Site, User
import datetime
from multiprocessing import Process
from utils.worker import worker
from scheduler import scheduler
import os


api_router = Blueprint(
    'api',
    __name__,
    url_prefix='/api'
)

@api_router.get('/site')
@login_required
def get_sites():
    session = create_session()
    user = flask_login.current_user
    sites = session.query(Site).filter(Site.user_id == user.id).all()
    return jsonify({
        'sites': [site.to_dict() for site in sites]
    })


@api_router.get('/site/<id>')
@login_required
def get_site(id):
    session = create_session()
    user = flask_login.current_user
    site = session.query(Site).filter(Site.id == id, Site.user_id == user.id).first()
    if not site: abort(404)
    return jsonify({
        'site': site.to_dict()
    })


@api_router.post('/site')
@login_required
def add_site():
    session = create_session()
    user = flask_login.current_user
    data = request.get_json()
    if session.query(Site).filter(Site.url == data['url']).first():
        return render_template('sites.html', title='Мои сайты', message='Такой сайт уже добавлен', form=form)
        
    id = datetime.datetime.now().timestamp()
    site = Site(
        id = int(id),
        name = data['name'],
        url = data['url'],
    )
    user.sites.append(site)
    session.merge(user)
    session.commit()

    scheduler.add_job(lambda: worker(site), 'interval', seconds=5, id=str(site.id))

    return jsonify({
        'message': 'OK'
    })


@api_router.put('/site/<id>')
@login_required
def edit_site(id):
    session = create_session()
    user = flask_login.current_user
    data = request.get_json()
    site = session.query(Site).filter(Site.id == id, Site.user == user).first()
    site.name = data['name']
    site.url = data['url']
    session.commit()

    return jsonify({
        'message': 'OK'
    })


@api_router.delete('/site/<id>')
@login_required
def remove_site(id):
    user = flask_login.current_user
    session = create_session()
    site = session.query(Site).filter(Site.id == id, Site.user == user).first()

    if not site: abort(404)

    session.delete(site)
    session.commit()

    if os.path.exists(f'userdata/icons/{site.id}.png'):
        os.remove(f'userdata/icons/{site.id}.png')

    scheduler.remove_job(site.id)

    return jsonify({
        'message': 'OK'
    })


@api_router.get('/site_icon/<id>')
def get_site_icon(id):
    path = f'userdata/icons/{id}.png'
    if os.path.isfile(path): return send_file(path)
    abort(404)