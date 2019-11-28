from flask import session
from flask_restful import Resource,reqparse
from database import db
from models.group import Group
from models.plate import Plate
from models.user import User
from utils import data_exist_validate, phone_validate, Response, login_first, success_msg, error_msg, manager_check
from datetime import datetime


class PlateService(Resource):
    @login_first
    @manager_check
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('perpage', type=int, location='args')
        query_data = parser.parse_args()

        # 初始化查询数据
        name = query_data.get('name')
        page = query_data.get('page') if query_data.get('page') else 1
        per_page = query_data.get('perpage') if query_data.get('perpage') else 10

        # 过滤删除的版块
        res_data = Plate.query.filter(Plate.status != -100)
        if name:
            res_data = res_data.filter(Plate.name.like('%{}%'.format(name)))

        # 分页返回,默认1， 10
        paginate_data = res_data.order_by(Plate.create_time.asc()).paginate(page, per_page)
        data = [p.output() for p in paginate_data.items]
        # data = [{"id": p.id, "name": p.name, "create_time": str(p.create_time)} for p in paginate_data.items]

        return Response.list_data(res_data.count(), paginate_data.page, data, success_msg.GET_OK)

    @login_first
    @manager_check
    def post(self):
        """
        版块
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument('plate', type=dict, location='json')
        args = parser.parse_args()
        plate_data = args.get('plate')

        # 数据校验
        name = plate_data.get('name')
        vl_result = data_exist_validate(name)
        if not vl_result.check:
            return Response.error(vl_result.msg)

        if Plate.get_by_name(name):
            return Response.error(error_msg.PLATE_EXIST)

        plate = Plate(name=name)
        try:
            db.session.add(plate)
            db.session.commit()
            result = Response.success(success_msg.ADD_OK)

        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result


class SinglePlate(Resource):
    @login_first
    def get(self, plate_id):

        plate = Plate.get_by_id(plate_id)
        if not plate:
            return Response.error(error_msg.PLATE_NULL)

        return Response.single_data(plate.output(), success_msg.GET_OK)

    @login_first
    @manager_check
    def patch(self, plate_id):

        parser = reqparse.RequestParser()
        parser.add_argument('plate', type=dict, location='json')
        args = parser.parse_args()
        plate_data = args.get('plate')

        # 数据校验
        name = plate_data.get('name')
        vl_result = data_exist_validate(name)
        if not vl_result.check:
            return Response.error(vl_result.msg)

        # 版块校验
        plate = Plate.get_by_id(plate_id)
        if not plate:
            return Response.error(error_msg.PLATE_NULL)

        # 存在校验
        old_plate = Plate.get_by_name(name)
        if old_plate and old_plate.id != plate_id:
            return Response.error(error_msg.PLATE_EXIST)

        try:
            plate.name = name
            plate.update_time = str(datetime.now())
            db.session.commit()
            result = Response.success(success_msg.PATCH_OK)
        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result

    @login_first
    @manager_check
    def delete(self, plate_id):
        plate = Plate.get_by_id(plate_id)
        if not plate:
            return Response.error(error_msg.PLATE_NULL)

        try:
            plate.delete()
            db.session.commit()
            result = Response.success(success_msg.DELETE_OK)
        except Exception as e:
            db.session.rollback()
            result = Response.error(e)

        return result