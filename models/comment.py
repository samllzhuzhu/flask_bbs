from datetime import datetime

from database import db


class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    content = db.Column(db.Text)
    pid = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    status = db.Column(db.Integer)

    def __init__(self, user_id, topic_id, content, pid=None):

        self.user_id = user_id
        self.topic_id = topic_id
        self.content = content
        self.pid = pid
        self.create_time = str(datetime.now())
        self.status = 0

    @staticmethod
    def get_by_id(com_id):
        return Comment.query.filter(Comment.id == com_id, Comment.status != -100).first()

    @staticmethod
    def get_by_topic_id(topic_id):
        return Comment.query.filter(Comment.topic_id == topic_id, Comment.status != -100,
                                    Comment.pid == None).all()

    def get_child_comments(self):
        return Comment.query.filter(Comment.pid == self.id, Comment.status != -100).all()

    def delete(self):
        self.status = -100

    def output(self):
        return {"id": self.id,
                "user_id": self.user_id,
                "topic_id": self.topic_id,
                "content": self.content,
                "create_time": str(self.create_time)}




