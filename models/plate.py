
from datetime import datetime
from database import db

# dadad
#DASFA
class Plate(db.Model):
    __tablename__ = 'plate' das

    id = db.Column(db.Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    status = db.Column(db.Integer)
    # topics = db.relationship('Topic', backref='plate', lazy='dynamic')

    def __init__(self, name, status=0):
        self.name = name
        self.create_time = str(datetime.now())
        self.status = status

    @staticmethod
    def get_by_id(id):
        return Plate.query.filter(Plate.id == id, Plate.status != -100).first()

    @staticmethod
    def get_by_name(name):
        return Plate.query.filter(Plate.name == name, Plate.status != -100).first()

    def delete(self):
        self.status = -100
        self.update_time = str(datetime.now())

    def output(self):
        return {'id': self.id,
                'name': self.name,
                'create_time': str(self.create_time)
                }