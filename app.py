from flask import Flask
import os
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from api import api
from database import db
import json


app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:xtyy123@127.0.0.1:3309/training?charset=utf8'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123123@192.168.91.146:3309/training?charset=utf8mb4'
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'tF5qrj2orUd/NWHSkW3VDc4ocNOjFhto'

api.init_app(app)
db.init_app(app)

# 跨域支持
def after_request(res):
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Method'] = '*'
    res.headers['Access-Control-Allow-Headers'] = '*'
    return res

app.after_request(after_request)

#
# migrate = Migrate(app, db)
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    # from models.user import User
    # from models.topic import Topic
    # from models.plate import Plate
    # from models.group import Group
    # from models.comment import Comment
    # manager.run()
    # app.run(debug=True, host='0.0.0.0', port='5000')
    app.run(debug=True)