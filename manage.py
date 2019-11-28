from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from app import app, db

from models.user import User
from models.topic import Topic
from models.plate import Plate
from models.group import Group
from models.comment import Comment

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':

    manager.run()
