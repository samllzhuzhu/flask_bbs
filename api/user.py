import json

from flask_restful import Resource,reqparse
from flask import session, request
from database import db
from models.group import Group
from models.user import User, user_role
from utils import data_exist_validate, phone_validate, Response, login_first, error_msg, success_msg, manager_check

##########
class UserService(Resource):

    def post(self):
        """
        注册用户
        :return:
        """

        parser = reqparse.RequestParser()
        parser.add_argument('user', type=dict, location='json')
        args = parser.parse_args()
        user_data = args.get('user')

        # 数据校验
        name = user_data.get('name')
        phone = user_data.get('phone')
        password = user_data.get('password')

        # 数据存在性校验
        result = data_exist_validate(name, phone, password)
        if not result.check:
            return Response.error(result.msg)

        # 手机号格式验证
        phone_result = phone_validate(phone)
        if not phone_result.check:
            return Response.error(phone_result.msg)

        # 用户是否存在
        if User.get_by_phone(user_data['phone']):
            return Response.error(error_msg.PHONE_EXIST)

        user = User(name=name, phone=phone, password=password)

        try:
            db.session.add(user)
            db.session.commit()
            result = Response.success(success_msg.USER_ADDED)

            # 设置状态保持
            session['id'] = user.id
            session['name'] = user.name
            session['phone'] = user.phone
            session['role'] = user.role

            # 设置redis
            # redis_store.hset('info', 'id', user.id)
            # redis_store.hset('info', 'role', user.role)
        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result


class SingleUser(Resource):

    @login_first
    def get(self, user_id):
        user = User.get_by_id(user_id)
        if not user:
            return Response.error(error_msg.USER_NULL)

        return Response.single_data(user.output(), success_msg.GET_OK)

    @login_first
    def patch(self, user_id):
        # if redis_store.hget('info', 'id') != user_id:
        if session.get('id') != user_id:
            return Response.error(error_msg.USER_ROLE_ERROR)

        parser = reqparse.RequestParser()
        parser.add_argument('user', type=dict, location='json')
        args = parser.parse_args()
        user_data = args.get('user')

        # 数据校验
        name = user_data.get('name')
        old_password = user_data.get('old_password')
        new_password = user_data.get('new_password')

        user = User.get_by_id(user_id)
        if not user:
            return Response.error(error_msg.USER_NULL)

        # 个人信息修改
        if old_password:
            if str(old_password) != str(user.password):
                return Response.error(error_msg.PASSWORD_ERROR)
            user.change_password(new_password)

        if name:
            user.change_name(name)

        try:
            db.session.commit()
            result = Response.success(success_msg.PATCH_OK)
        except Exception as e:
            db.session.rollback()
            result = Response.error(e)
        return result
            

class AdminService(Resource):
    @login_first
    @manager_check
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='args')
        parser.add_argument('group', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('perpage', type=int, location='args')
        query_data = parser.parse_args()

        # 初始化查询数据
        name = query_data.get('name')
        role = query_data.get('role')
        group_id = query_data.get('group')
        page = query_data.get('page') if query_data.get('page') else 1
        per_page = query_data.get('perpage') if query_data.get('perpage') else 10

        # 筛选过滤条件
        users = User.query.filter(User.status != -100)
        if name:
            users = users.filter(User.name.like('%{}%'.format(name)))
        if role:
            users = users.filter(User.role == role)
        if group_id:
            users = users.filter(User.group_id == group_id)

        user_data = users.order_by(User.create_time.asc()).paginate(page, per_page)

        # 格式化输出
        data = [p.output() for p in user_data.items]

        return Response.list_data(users.count(), user_data.page, data, success_msg.GET_OK)

    @login_first
    @manager_check
    def patch(self):

        parser = reqparse.RequestParser()
        parser.add_argument('user', type=dict, location='json')
        args = parser.parse_args()
        user_data = args.get('user')

        # 数据校验
        user_id = user_data.get('id')
        role = user_data.get('role')

        # 数据存在性校验
        result = data_exist_validate(user_id, role)
        if not result.check:
            return Response.error(result.msg)

        if role not in [user_role.MANAGER, user_role.NORMAL]:
            return Response.error(error_msg.ROLE_ERROR)

        user = User.get_by_id(user_id)
        if not user:
            return Response.error(error_msg.USER_NULL)

        try:
            user.role = role
            db.session.commit()
            result = Response.success(success_msg.PATCH_OK)
        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result

    @login_first
    @manager_check
    def delete(self):

        parser = reqparse.RequestParser()
        parser.add_argument('user', type=dict, location='json')
        args = parser.parse_args()
        user_data = args.get('user')

        # 用户校验
        user_id = user_data.get('id')
        user = User.get_by_id(user_id)
        if not user:
            return Response.error(error_msg.USER_NULL)

        try:
            user.delete()
            db.session.commit()
            result = Response.success(success_msg.DELETE_OK)
        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result


class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user', type=dict, location='json')
        args = parser.parse_args()
        user_data = args.get('user')

        # 数据校验
        phone = user_data.get('phone')
        password = user_data.get('password')

        # 数据存在性校验
        result = data_exist_validate(phone, password)
        if not result.check:
            return Response.error(result.msg)

        user = User.login_check(phone, password)
        if not user:
            return Response.error(error_msg.PHONE_PASSWORD_ERROR)

        # 设置状态保持
        session['id'] = user.id
        session['name'] = user.name
        session['phone'] = user.phone
        session['role'] = user.role
        #
        # redis_store.hset('info', 'id', user.id)
        # redis_store.hset('info', 'role', user.role)

        result = Response.success(success_msg.LOGIN_SUCCESS)
        return result

    def delete(self):
        """
        清除session
        :return:
        """
        try:
            session.pop('id')
            session.pop('name')
            session.pop('phone')
            session.pop('role')

            # redis_store.delete('info')

            result = Response.success(success_msg.LOGIN_EXIT)

        except Exception as e:
            result = Response.error('退出成功')

        return result



















