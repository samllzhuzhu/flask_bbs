from flask_restful import Api
from api.comment import CommentService, SingleComment
from api.group import GroupService, GroupUser
from api.plate import PlateService, SinglePlate
from api.topic import TopicService, SingleTopic
from api.user import UserService, SingleUser, UserLogin, AdminService

api = Api()

# user
api.add_resource(UserLogin, '/login')
api.add_resource(UserService, '/users')
api.add_resource(SingleUser, '/user/<int:user_id>')
api.add_resource(AdminService, '/m/users')

# plate
api.add_resource(PlateService, '/plates')
api.add_resource(SinglePlate, '/plate/<int:plate_id>')

# topic
api.add_resource(TopicService, '/topics')
api.add_resource(SingleTopic, '/topic/<int:topic_id>')

# group
api.add_resource(GroupService, '/groups')
api.add_resource(GroupUser, '/group/<int:group_id>/user/<int:user_id>')

# comment
api.add_resource(CommentService, '/topic/<int:topic_id>/comments')
api.add_resource(SingleComment, '/comment/<int:com_id>')