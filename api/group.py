from flask_restful import Resource,reqparse
from flask import session
from database import db
from models.comment import Comment
from models.group import Group
from models.plate import Plate
from models.topic import Topic
from models.user import User, user_role
from utils import data_exist_validate, phone_validate, Response, login_first, success_msg, error_msg, manager_check
# 不错
# 可以
# 还行
# dafadasfa
class GroupService(Resource):
    """1211"""
    @login_first
    @manager_check
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('group', type=dict, location='json')
        args = parser.parse_args()
        group_data = args.get('group')

        group_name = group_data.get('name')
        group_role = group_data.get('role')

        if group_role not in [user_role.MANAGER, user_role.NORMAL]:
            return Response.error(error_msg.ROLE_ERROR)

        if Group.get_by_name(group_name):
            return Response.error(error_msg.GROUP_EXIST)

        group = Group(group_name, group_role)

        try:
            db.session.add(group)
            db.session.commit()
            result = Response.success(success_msg.ADD_OK)
        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result

    @login_first
    @manager_check
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('perpage', type=int, location='args')
        query_data = parser.parse_args()

        # 初始化查询数据
        page = query_data.get('page') if query_data.get('page') else 1
        per_page = query_data.get('perpage') if query_data.get('perpage') else 10

        group_data = Group.query.filter(Group.status != -100).order_by(Group.create_time.desc())
        pg_data = group_data.paginate(page, per_page)
        data = [g.output() for g in pg_data.items]

        return Response.list_data(group_data.count(), pg_data.page, data, success_msg.GET_OK)


class GroupUser(Resource):

    @login_first
    @manager_check
    def post(self, group_id, user_id):
        """
        添加用户进分组
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument('group', type=dict, location='json')
        args = parser.parse_args()
        group_data = args.get('group')

        group = Group.get_by_id(group_id)
        if not group:
            return Response.error(error_msg.GROUP_NULL)

        # user_id = group_data.get('user_id')

        user = User.get_by_id(user_id)
        if not user:
            return Response.error(error_msg.USER_NULL)

        # 加入分组
        user.add_group(group_id, group.group_role)

        try:
            db.session.commit()
            result = Response.success(success_msg.OPRATE_SUCCESS)
        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result

    @login_first
    @manager_check
    def delete(self, group_id, user_id):

        parser = reqparse.RequestParser()
        parser.add_argument('group', type=dict, location='json')
        args = parser.parse_args()
        group_data = args.get('group')

        group = Group.get_by_id(group_id)
        if not group:
            return Response.error(error_msg.GROUP_NULL)

        # user_id = group_data.get('user_id')

        user = User.get_by_id(user_id)
        if not user:
            return Response.error(error_msg.USER_NULL)

        # 退出分组
        user.exit_group()

        try:
            db.session.commit()
            result = Response.success(success_msg.OPRATE_SUCCESS)
        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result




