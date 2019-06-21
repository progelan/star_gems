from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin# is_authenticated, is_active, is_anonymous
from sqlalchemy.orm import relationship
from datetime import datetime


class Preference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gem_type = db.Column(db.String(64), nullable=False)
    gem_rate = db.Column(db.Float, default=0)
    elf_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    elf = relationship("User", backref=db.backref('preferences', order_by=gem_rate, lazy='dynamic'))

    def __repr__(self):
        return '<Preference {}:{} ~ {}>'.format(self.elf, self.gem_type, round(self.gem_rate, 2))

    def __str__(self):
        return self.gem_type



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64), nullable=False)
    character = db.Column(db.String(64), nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Boolean, default=True)
    deletion_date = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.username)# строковое представление имени юзера

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)# генерит хэш-пароль из пароля

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)# сверяет хэш-пароли

    def avatar(self):
        return '../static/{}.png'.format(self.character)# возвращает путь к аватарке


class Gem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(64), default='mined')
    mined_date = db.Column(db.DateTime, default=datetime.utcnow)
    assignation_type = db.Column(db.String(64))
    assigned_date = db.Column(db.DateTime)
    confirmation_date = db.Column(db.DateTime)
    gnome_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    elf_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    master_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    gnome = relationship("User", foreign_keys=[gnome_id], backref=db.backref('gnome_gems', lazy='dynamic'))
    elf = relationship("User", foreign_keys=[elf_id], backref=db.backref('elf_gems', lazy='dynamic'))
    master = relationship("User", foreign_keys=[master_id], backref=db.backref('master_gems', lazy='dynamic'))

    def __repr__(self):
        return '<Gem: {}, {}>'.format(self.type, self.status)


class TypeGem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64), nullable=False, unique=True)

    def __repr__(self):
        return '<Type gem: {}>'.format(self.type)


class Requirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    req_type = db.Column(db.String(64), nullable=False, unique=True)
    req_rate = db.Column(db.Float, default=0)

    def __repr__(self):
        return '<Requirement {} ~ {}>'.format(self.req_type, round(self.req_rate, 2))
