from db.db_session import create_session
import flask_login
from multiprocessing import Process
from db.models import User, Site
from utils.worker import worker

def load_processes(scheduler):
    session = create_session()
    sites = session.query(Site).all()
    if sites:
        for site in sites:
            scheduler.add_job(lambda: worker(site), 'interval', seconds=5, id=str(site.id))
        
    scheduler.start()