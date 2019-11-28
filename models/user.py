from datetime import datetime
from utils import enum
from database import db

# 用户角色
user_role = enum(MANAGER='manager', NORMAL='normal')


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    create_time = db.Column(db.DateTime)
    status = db.Column(db.Integer)
    # topics = db.relationship('Topic', backref='user', lazy='dynamic')
    # comments = db.relationship('Comment', backref='user', lazy='dynamic')

    def __init__(self, name, phone, password, role=user_role.NORMAL, group_id=None, status=0):
        self.name = name
        self.phone = phone
        self.password = password
        self.role = role
        self.group_id = group_id
        self.create_time = str(datetime.now())
        self.status = status

    @staticmethod
    def get_by_id(id):
        return User.query.filter(User.id == id, User.status != -100).first()

    @staticmethod
    def get_by_phone(phone):
        return User.query.filter(User.phone == phone, User.status != -100).first()

    @staticmethod
    def login_check(phone, password):
        return User.query.filter(User.phone == phone, User.password == password).first()

    def add_group(self, group_id, role):
        self.group_id = group_id
        self.role = role

    def exit_group(self):
        self.group_id = None
        self.role = 'normal'

    def change_password(self, password):
        self.password = password

    def change_name(self, name):
        self.name = name

    def delete(self):
        self.status = -100

    def output(self):
        return {"id": self.id,
                "name": self.name,
                "phone": self.phone,
                "role": self.role,
                "create_time": str(self.create_time),
                "group_name": self.group.group_name if self.group else ''
                }
