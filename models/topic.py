from datetime import datetime

from database import db
from utils import enum

great_code = enum(GREAT=1, NOGREAT=0)

class Topic(db.Model):
    __tablename__ = 'topic'

    id = db.Column(db.Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    title = db.Column(db.String(20), nullable=False)
    plate_id = db.Column(db.Integer, db.ForeignKey('plate.id'))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_great = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    status = db.Column(db.Integer)
    # comments = db.relationship('Comment', backref='topic', lazy='dynamic')

    def __init__(self, title, plate_id, content, user_id, is_great=0, status=0):
        self.title = title
        self.plate_id = plate_id
        self.content = content
        self.user_id = user_id
        self.is_great = is_great
        self.create_time = str(datetime.now())
        self.status = status

    @staticmethod
    def get_by_id(topic_id):
        return Topic.query.filter(Topic.id == topic_id,
                           Topic.status != -100).first()

    def add_great(self):
        self.is_great = great_code.GREAT

    def cancle_great(self):
        self.is_great = great_code.NOGREAT

    def delete(self):
        self.status = -100
        self.update_time = str(datetime.now())

    def output(self):
        return {'id': self.id,
                'title': self.title,
                'content': self.content,
                'is_great': self.is_great,
                'create_time': str(self.create_time)}



