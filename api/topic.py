from flask_restful import Resource,reqparse
from flask import session
from database import db
from models.group import Group
from models.plate import Plate
from models.topic import Topic, great_code
from models.user import User, user_role
from utils import data_exist_validate, phone_validate, Response, login_first, success_msg, error_msg, manager_check


####DDD
class TopicService(Resource):
    @login_first
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, location='args')
        parser.add_argument('is_great', type=int, location='args')
        parser.add_argument('sort', type=int, location='args')
        parser.add_argument('count', type=int, location='args')
        parser.add_argument('plate', type=int, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('perpage', type=int, location='args')
        query_data = parser.parse_args()

        title = query_data.get('title')
        is_great = query_data.get('is_great')
        sort = query_data.get('sort')
        count = query_data.get('count')
        plate = query_data.get('plate')
        page = query_data.get('page') if query_data.get('page') else 1
        per_page = query_data.get('perpage') if query_data.get('perpage') else 10
        data = db.session.query(Topic, Plate.name, User.name).join(Plate, Plate.id == Topic.plate_id).join(User, User.id == Topic.user_id).filter(Topic.status!=-100)

        if title:
            data = data.filter(Topic.title.like('%{}%'.format(title)))

        if is_great:
            data = data.filter(Topic.is_great == is_great)
        if plate:
            data = data.filter(Topic.plate_id == plate)

        if sort:
            data = data.order_by(Topic.create_time.asc())
        else:
            data = data.order_by(Topic.create_time.desc())

        # 分页后的数据
        pg_data = data.paginate(page, per_page)

        result = []
        for p in pg_data.items:
            tp_data = p[0].output()
            tp_data['user_name'] = p[2]
            tp_data['plate'] = p[1]
            result.append(tp_data)

        return Response.list_data(data.count(), pg_data.page, result, success_msg.GET_OK)

    @login_first
    def post(self):
        """
        发帖
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument('topic', type=dict, location='json')
        args = parser.parse_args()
        topic_data = args.get('topic')

        # 数据校验
        title = topic_data.get('title')
        plate_id = topic_data.get('plate_id')
        content = topic_data.get('content')

        vl_result = data_exist_validate(title, plate_id, content)
        if not vl_result.check:
            return Response.error(vl_result.msg)

        # 版块校验
        if not Plate.get_by_id(plate_id):
            return Response.error(error_msg.PLATE_NULL)

        user_id = session.get('id')
        # user_id = redis_store.hget('info', 'id')
        topic = Topic(title, plate_id, content, user_id)

        try:
            db.session.add(topic)
            db.session.commit()
            result = Response.success(success_msg.ADD_OK)

        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result


class SingleTopic(Resource):

    @login_first
    def get(self, topic_id):
        topic = Topic.get_by_id(topic_id)
        if not topic:
            return Response.error(error_msg.TOPIC_NULL)
        plate_name = Plate.query.with_entities(Plate.name).filter(Plate.id == topic.plate_id).first()
        user_name = Plate.query.with_entities(User.name).filter(User.id == topic.user_id).first()
        result = topic.output()
        result['plate'] = plate_name[0]
        result['user_name'] = user_name[0]
        # result = {'id': topic.id, 'user_name': user_name[0], 'title': topic.title, 'content': topic.content, 'is_great': topic.is_great, 'plate': plate_name[0]}
        return Response.single_data(result, success_msg.GET_OK)

    @login_first
    @manager_check
    def patch(self, topic_id):

        parser = reqparse.RequestParser()
        parser.add_argument('topic', type=dict, location='json')
        args = parser.parse_args()
        topic_data = args.get('topic')
        is_great = topic_data.get('is_great')

        if int(is_great) not in [great_code.GREAT, great_code.NOGREAT]:
            return Response.error(error_msg.OPRATE_ERROR)

        topic = Topic.get_by_id(topic_id)
        if not topic:
            return Response.error(error_msg.TOPIC_NULL)

        if is_great == great_code.GREAT:
            topic.add_great()
        else:
            topic.cancle_great()

        try:
            db.session.commit()
            result = Response.success(success_msg.OPRATE_SUCCESS)
        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result

    @login_first
    def delete(self, topic_id):
        topic = Topic.get_by_id(topic_id)
        if not topic:
            return Response.error(error_msg.TOPIC_NULL)
        # user_id = redis_store.hget('info', 'id')
        user_id = session.get('id')
        role = session.get('id')
        # role = redis_store.hget('info', 'role')
        if user_id != topic.user_id or  role != user_role.MANAGER:
            return Response.error(error_msg.DELETE_ERROR)

        topic.delete()

        try:
            db.session.commit()
            result = Response.success(success_msg.DELETE_OK)
        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result








