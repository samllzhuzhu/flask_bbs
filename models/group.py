from datetime import datetime

from database import db


class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    group_name = db.Column(db.String(20), nullable=False)
    group_role = db.Column(db.String(20))
    create_time = db.Column(db.DateTime)
    status = db.Column(db.Integer)
    users = db.relationship('User', backref='group', lazy='dynamic')

    def __init__(self, name, role, status=0):
        self.group_name = name
        self.group_role = role
        self.create_time = str(datetime.now())
        self.status = status

    @staticmethod
    def get_by_id(group_id):
        return Group.query.filter(Group.id == group_id, Group.status != -100).first()

    @staticmethod
    def get_by_name(name):
        return Group.query.filter(Group.group_name == name, Group.status != -100).first()

    def output(self):
        return {'id': self.id,
                'group_name': self.group_name,
                'group_role': self.group_role,
                }




