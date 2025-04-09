import datetime
from db.db_session import SqlAlchemyBase
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Site(SqlAlchemyBase):
    __tablename__ = 'sites'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', lazy='subquery')

    created_date = Column(DateTime, default=datetime.datetime.now)

    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'user_id': self.user_id,
            'user': self.user.to_dict(),
            'created_date': self.created_date
        }

class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    sites = relationship('Site', back_populates='user', lazy='subquery')
    created_date = Column(DateTime, default=datetime.datetime.now)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_date': self.created_date
        },