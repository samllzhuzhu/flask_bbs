import re
from flask import session
import json
import redis

# redis
# redis_store = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

class Vld(object):
    def __init__(self, status, msg=''):
        self.check = status
        self.msg = msg


def data_exist_validate(*data):
    """
    数据存在性验证
    :param data:
    :return:
    """
    if not all(data):
        return Vld(False, '缺少必要参数')
    return Vld(True)


def phone_validate(phone):
    """
    手机号格式验证
    :param phone: 手机号
    :return:
    """
    # 手机号格式验证
    if len(phone) != 11 or not str(phone).isdigit():
        return Vld(False, '手机号格式错误')

    res = re.match(r"^1[345678]\d{9}$", phone)
    if not res:
        return Vld(False, '无效手机号')
    return Vld(True)


# 返回信息
class Response(object):

    @staticmethod
    def success(msg=''):
        return {'Success': True, "msg": msg}

    @staticmethod
    def error(msg=''):
        return {'Success': False, "msg": msg}

    @staticmethod
    def single_data(data='', msg=''):
        return {'Success': True, 'data': data,'msg': msg}

    @staticmethod
    def list_data(count, page, data='', msg=''):
        return {'Success': True, "count": count,
                'page': page, 'data': data, "msg": msg}


# 验证登录
def login_first(func):
    def wrapper(*args, **kwargs):
        # if not redis_store.hget('info', 'id'):
        if not session.get('id'):
            return Response.error('请先登录')
        return func(*args, **kwargs)
    return wrapper


# 管理员身份验证
def manager_check(func):
    def wrapper(*args, **kwargs):
        # role = redis_store.hget('info', 'role')
        role = session.get('role')
        if role != 'manager':
            return Response.error('非管理员权限')
        return func(*args, **kwargs)
    return wrapper


# 自定义的枚举
def enum(**status):
    return type('Enum', (), status)


error_msg = enum(LOGIN_ERROR='请先登录',
                 PHONE_ERROR='手机号格式错误',
                 PHONE_PASSWORD_ERROR='手机号或密码错误',
                 PARAMS_ERROR='缺少必要参数',
                 PHONE_EXIST='该手机号已被注册',
                 USER_ADDED_FAILD='新增用户失败',
                 USER_NULL='用户不存在',
                 USER_ROLE_ERROR='无权限修改他人信息',
                 PASSWORD_ERROR='老密码验证错误',
                 MANAGER_ROLE_ERROR='非管理员权限',
                 ROLE_ERROR='权限错误',
                 PLATE_NULL='该版块不存在',
                 PLATE_EXIST='该版块存在',
                 TOPIC_NULL='帖子不存在',
                 OPRATE_ERROR='无效操作',
                 DELETE_ERROR='无权删除帖子',
                 GROUP_EXIST='该组已存在',
                 GROUP_NULL='分组不存在',
                 COMMENT_NULL='评论不存在',
                 COMMENT_DELETE_ROLE='无权删除评论',
                 )

success_msg = enum(USER_ADDED='新增用户成功',
                   ADD_OK='新增成功',
                   GET_OK='数据获取成功',
                   PATCH_OK='修改成功',
                   DELETE_OK='删除成功',
                   LOGIN_SUCCESS='登录成功',
                   LOGIN_EXIT='退出成功',
                   OPRATE_SUCCESS='操作成功',
                   )

