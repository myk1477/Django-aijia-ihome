import datetime
import json
import logging

from django import http
from django.utils.decorators import method_decorator
from django.views import View
from django_redis import get_redis_connection

from apps.homes.models import House
from apps.order.models import Order
from utils.decorators import login_required
from utils.response_code import RET

logger = logging.getLogger("django")


class OrdersView(View):
    """
    订单
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrdersView, self).dispatch(*args, **kwargs)

    def get(self, request):
        user = request.user
        role = request.GET.get('role')

        if not role:
            return http.JsonResponse({"errno": RET.PARAMERR, "errmsg": "参数错误"})

        if role not in ["landlord", "custom"]:
            return http.JsonResponse({"errno": RET.PARAMERR, "errmsg": "参数错误"})

        if role == "custom":
            # 查询当前自己下了哪些订单
            orders = Order.objects.filter(user=user).order_by("-create_time")
        else:
            # 查询自己房屋都有哪些订单
            houses = House.objects.filter(user=user)
            house_ids = [house.id for house in houses]
            orders = Order.objects.filter(house_id__in=house_ids).order_by("-create_time")

        orders_dict = [order.to_dict() for order in orders]
        print(orders_dict)
        return http.JsonResponse({"errno": RET.OK, "errmsg": "发布成功", "data": {"orders": orders_dict}})

    def post(self, request):
        # 获取到当前用户的id
        user = request.user
        # 获取到传入的参数
        dict_data = json.loads(request.body.decode())

        house_id = dict_data.get('house_id')
        start_date_str = dict_data.get('start_date')
        end_date_str = dict_data.get('end_date')

        # 校验参数
        if not all([house_id, start_date_str, end_date_str]):
            return http.JsonResponse({"errno": RET.PARAMERR, "errmsg": "参数错误"})

        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
            assert start_date < end_date, Exception('开始日期大于结束日期')
            # 计算出入住天数
            days = (end_date - start_date).days
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"errno": RET.PARAMERR, "errmsg": "参数错误"})

        # 判断房屋是否存在
        try:
            house = House.objects.get(id=house_id)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"errno": RET.NODATA, "errmsg": "房屋不存在"})

        # 判断房屋是否是当前登录用户的
        if user.id == house.user.id:
            return http.JsonResponse({"errno": RET.ROLEERR, "errmsg": "不能订购自己的房间"})

        # 查询是否存在冲突的订单
        try:
            filters = {"house": house, "begin_date__lt": end_date, "end_date__gt": start_date}
            count = Order.objects.filter(**filters).count()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"errno": RET.DBERR, "errmsg": "数据库查询错误"})

        if count > 0:
            return http.JsonResponse({"errno": RET.DATAERR, "errmsg": "房间已经被预定"})

        amount = days * house.price
        # 生成订单的模型
        order = Order()
        order.user = user
        order.house = house
        order.begin_date = start_date
        order.end_date = end_date
        order.days = days
        order.house_price = house.price
        order.amount = amount

        try:
            order.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"errno": RET.DBERR, "errmsg": "数据库保存失败"})

        return http.JsonResponse({"errno": RET.OK, "errmsg": "发布成功", "data": {"order_id": order.pk}})


class OrdersStatusView(View):
    """
    接单和拒单
    """
    @method_decorator(login_required)
    def put(self, request, order_id):
        user = request.user

        dict_data = json.loads(request.body.decode())
        action = dict_data.get('action')
        if action not in ("accept", "reject"):
            return http.JsonResponse({"errno": RET.PARAMERR, "errmsg": "参数错误"})

        try:
            order = Order.objects.filter(id=order_id, status=Order.ORDER_STATUS["WAIT_ACCEPT"]).first()
            house = order.house
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"errno": RET.DBERR, "errmsg": "查询数据错误"})

        # 判断订单是否存在并且当前房屋的用户id是当前用户的id
        if not order or house.user != user:
            return http.JsonResponse({"errno": RET.NODATA, "errmsg": "数据有误"})

        if action == "accept":
            # 接单
            order.status = Order.ORDER_STATUS["WAIT_COMMENT"]
        elif action == "reject":
            # 获取拒单原因
            reason = dict_data.get("reason")
            if not reason:
                return http.JsonResponse({"errno": RET.PARAMERR, "errmsg": "未填写拒绝原因"})


            # 设置状态为拒单并且设置拒单原因
            order.status = Order.ORDER_STATUS["REJECTED"]
            order.comment = reason

        # 保存到数据库
        try:
            order.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"errno": RET.DBERR, "errmsg": "保存订单状态失败"})

        return http.JsonResponse({"errno": RET.OK, "errmsg": "ok"})