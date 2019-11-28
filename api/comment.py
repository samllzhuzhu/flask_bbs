# from utils import redis_store
from flask_restful import Resource,reqparse
from flask import session
from database import db
from models.comment import Comment
from models.group import Group
from models.plate import Plate
from models.topic import Topic
from models.user import User
from utils import data_exist_validate, phone_validate, Response, login_first, success_msg, error_msg


class CommentService(Resource):
    @login_first
    def post(self, topic_id):
        topic = Topic.get_by_id(topic_id)
        if not topic:
            return Response.error(error_msg.TOPIC_NULL)

        parser = reqparse.RequestParser()
        parser.add_argument('comment', type=dict, location='json')
        args = parser.parse_args()
        comment_data = args.get('comment')

        content = comment_data.get('content')
        pid = comment_data.get('pid')

        # 回复评论
        if pid:
            p_comment = Comment.get_by_id(pid)

            if not p_comment:
                return Response.error(error_msg.COMMENT_NULL)

        # comment = Comment(redis_store.hget('info', 'id'), topic_id, content, pid if pid else None)
        comment = Comment(session.get('id'), topic_id, content, pid if pid else None)

        try:
            db.session.add(comment)
            db.session.commit()
            result = Response.success(success_msg.OPRATE_SUCCESS)

        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result

    @login_first
    def get(self, topic_id):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('perpage', type=int, location='args')
        query_data = parser.parse_args()

        # 初始化查询数据
        page = query_data.get('page') if query_data.get('page') else 1
        per_page = query_data.get('perpage') if query_data.get('perpage') else 10

        topic = Topic.get_by_id(topic_id)
        if not topic:
            return Response.error(error_msg.TOPIC_NULL)

        # comments = Comment.get_by_topic_id(topic_id)

        data = Comment.query.filter(Comment.topic_id == topic_id, Comment.status != -100,
                                    Comment.pid == None)

        pg_data = data.paginate(page, per_page)

        res_list = []
        for p in pg_data.items:
            user = User.get_by_id(p.user_id)
            p_dict = p.output()
            p_dict['user_name'] = user.name
            child_list = []
            com_childs = p.get_child_comments()
            for cd in com_childs:
                c_user = User.get_by_id(cd.user_id)
                c_dict = cd.output()
                c_dict['user_name'] = c_user.name
                child_list.append(c_dict)
            p_dict['child_comments'] = child_list

            res_list.append(p_dict)

        return Response.list_data(data.count(), pg_data.page, res_list, success_msg.GET_OK)


class SingleComment(Resource):
    @login_first
    def delete(self, com_id):
        comment = Comment.get_by_id(com_id)
        if not comment:
            return Response.error(error_msg.COMMENT_NULL)

        # if redis_store.hget('info', 'id') != comment.user_id:
        if session.get('id') != comment.user_id:
            return Response.error(error_msg.COMMENT_DELETE_ROLE)

        try:
            comment.delete()
            db.session.commit()
            result = Response.success(success_msg.OPRATE_SUCCESS)

        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result




