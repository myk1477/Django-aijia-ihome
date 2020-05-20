import datetime

from django import http
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views import View
from django.db import DatabaseError
from django.core.cache import cache
from django.db import transaction
from django.conf import settings
from django_redis import get_redis_connection

from apps.homes.models import Area, House, Facility, HouseImage
from libs.qiniu.qiniu_storage import storage
from apps.order.models import Order
from utils import constants
from utils.decorators import login_required
from utils.param_checking import image_file
from utils.response_code import RET
import logging
import json
logger = logging.getLogger("django")

# 获取城区列表
class AreaView(View):
    # 因为地址会经常被查询,在这里使用缓存
    def get(self,request):
        # 获取缓存的数据
        area_cache = cache.get('area')
        if not area_cache:
            # 若是缓存中没有 则查询数据库并且保存到数据库
            try:
                # 防止 查询数据库出现错误
                areas = Area.objects.all()
            except DatabaseError as e:
                logger.error(e)
                return http.JsonResponse({"errno": RET.DBERR, "errmsg": "数据库查询失败"})
            # 使用 列表推导式(代替下面的for循环) 构造 data需要的数据
            area_cache = [area.to_dict() for area in areas]
            # 把地址 添加到缓存中
            cache.set('area',area_cache,constants.AREA_INFO_REDIS_EXPIRES)
        # for area in areas:
        #     data.append(area.to_dict())

        return http.JsonResponse({
            "errmsg": "获取成功",
            "errno": RET.OK,
            "data":area_cache
        })



# 首页房屋推荐的获取
class IndexView(View):
    def get(self,request):
        # 使用切片获取 五间房屋的数据
        # 应该 对其进行排序 选择排名靠前的五家  按照该房屋的订单数进行排序
        try:
            hoses = houses = House.objects.order_by("-order_count")[0:5]
        except DatabaseError as e:
            logger.error(e)
            return http.JsonResponse({"errno": RET.DBERR, "errmsg": "数据库查询失败"})
        # 构造返回的数据
        data = [hose.to_basic_dict() for hose in hoses]

        return http.JsonResponse({
            'data': data,
            'errmsg':'ok',
            'errno':RET.OK

        })

# 房屋的详情页面
class DetailView(View):
    def get(self,request,house_id):
        # 获取 房间 信息
        try:
            house = House.objects.get(id=house_id)
        except DatabaseError as e :
            logger.error(e)
            return http.JsonResponse({"errno": RET.DBERR, "errmsg": "数据库查询失败"})
        # 判断是否是登录用户
        user = request.user
        if user.is_authenticated:
            # 若是登录用户
            user_id = 1

        else:
            # 若不是登录用户
            user_id = -1

        # 返回响应
        return http.JsonResponse({'errmsg':'ok','errno':RET.OK,
                                      'data':{'user_id':user_id,'house':house.to_full_dict()}})

# 展示用户发布的房源  即 我的房屋列表的实现
class ShowReleaseView(View):
    @method_decorator(login_required)
    def get(self,request):
        user = request.user
        # 获取当前用户发布的房源
        houses = [house.to_basic_dict() for house in House.objects.filter(user=user)]
        return http.JsonResponse({"errno": RET.OK, "errmsg": '发布房源查询成功', "data": {'houses':houses}})


class ReleaseHouseView(View):
    # 房屋数据搜素
    def get(self,request):
        # 获取所有的参数
        args = request.GET
        area_id = args.get('aid', '')
        start_date_str = args.get('sd', '')
        end_date_str = args.get('ed', '')
        # booking(订单量), price-inc(低到高), price-des(高到低),
        sort_key = args.get('sk', 'new')
        page = args.get('p', '1')

        try:
            page = int(page)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"errno": RET.PARAMERR, "errmsg": "参数错误"})

        # redis_conn = get_redis_connection("house_cache")
        # try:
        #     redis_key = "houses_%s_%s_%s_%s" % (area_id, start_date_str, end_date_str, sort_key)
        #     data = redis_conn.hget(redis_key, page)
        #     if data:
        #         return http.JsonResponse({"errno": RET.OK, "errmsg": "OK", "data": json.loads(data)})
        # except Exception as e:
        #     logger.error(e)

        # 对日期进行相关处理
        try:
            start_date = None
            end_date = None
            if start_date_str:
                start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            if end_date_str:
                end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
            # 如果开始时间大于或者等于结束时间,就报错
            if start_date and end_date:
                assert start_date < end_date, Exception('开始时间大于结束时间')
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"errno": RET.PARAMERR, "errmsg": "参数错误"})

        filters = {}

        # 如果区域id存在
        if area_id:
            filters["area_id"] = area_id

        # 定义数组保存冲突的订单
        if start_date and end_date:
            # 如果订单的开始时间 < 结束时间 and 订单的结束时间 > 开始时间
            conflict_order = Order.objects.filter(begin_date__lt=end_date, end_date__gt=start_date)
        elif start_date:
            # 订单的结束时间 > 开始时间
            conflict_order = Order.objects.filter(end_date__gt=start_date)
        elif end_date:
            # 订单的开始时间 < 结束时间
            conflict_order = Order.objects.filter(begin_date__lt=end_date)
        else:
            conflict_order = []

        # 取到冲突订单的房屋id
        conflict_house_id = [order.house_id for order in conflict_order]
        # 添加条件:查询出来的房屋不包括冲突订单中的房屋id
        # TODO：不在列表中未处理，先用in来代替下
        if conflict_house_id:
            filters["id__in"] = conflict_house_id

        # 查询数据
        if sort_key == "booking":
            # 订单量从高到低
            houses_query = House.objects.filter(**filters).order_by("-order_count")
        elif sort_key == "price-inc":
            # 价格从低到高
            houses_query = House.objects.filter(**filters).order_by("price")
        elif sort_key == "price-des":
            # 价格从高到低
            houses_query = House.objects.filter(**filters).order_by("-price")
        else:
            # 默认以最新的排序
            houses_query = House.objects.filter(**filters).order_by("-create_time")

        paginator = Paginator(houses_query, constants.HOUSE_LIST_PAGE_CAPACITY)
        # 获取当前页对象
        page_houses = paginator.page(page)
        # 获取总页数
        total_page = paginator.num_pages

        houses = [house.to_basic_dict() for house in page_houses]

        data = {
            "total_page": total_page,
            "houses": houses
        }

        if page <= total_page:
            try:
                # 生成缓存用的key
                redis_key = "houses_%s_%s_%s_%s" % (area_id, start_date_str, end_date_str, sort_key)
                # 获取 redis_store 的 pipeline 对象,其可以一次可以做多个redis操作
                pl = get_redis_connection.pipeline()
                # 开启事务
                pl.multi()
                # 缓存数据
                pl.hset(redis_key, page, json.dumps(data))
                # 设置保存数据的有效期
                pl.expire(redis_key, constants.HOUSE_LIST_REDIS_EXPIRES)
                # 提交事务
                pl.execute()
            except Exception as e:
                logger.error(e)

        return http.JsonResponse({"errno": RET.OK, "errmsg": "OK", "data": data})
    # 发布房源
    @method_decorator(login_required)
    def post(self,request):
        user = request.user
        # 获取数据  前端发送的数据类型是json字符串
        data = json.loads(request.body.decode())
        title = data.get('title')    # 标题
        price = data.get('price')    # 价格
        area_id = data.get('area_id')   # 城区id
        address = data.get('address')   # 房屋地址
        room_count = data.get('room_count')   # 房屋数目
        acreage = data.get('acreage')    # 房屋面积
        unit = data.get('unit')     # 房屋单元，如：几室几厅
        capacity = data.get('capacity')    # 房屋容纳的人数
        beds = data.get('beds')     # 房屋床铺的配置
        deposit = data.get('deposit')     #  房屋押金
        min_days = data.get('min_days')   # 最少入住天数
        max_days = data.get('max_days')   #  最大入住天数，0表示不限制
        # 类型是列表可能为空 不需要去判断这个数据是否存在
        facility_ids = data.get('facility')   #  用户选择的设施信息id列表，如：[7, 8]
        # 验证数据
        if not all([title,price,area_id,address,room_count,acreage,unit,
                    capacity,beds,deposit,min_days,max_days]):
            return http.JsonResponse({"errno": RET.PARAMERR, "errmsg": "参数错误"})
        # 最少入住天数不能小于0
        if eval(min_days) < 0 or eval(max_days) < 0:
            return http.JsonResponse({"errno": RET.PARAMERR, "errmsg": "参数错误"})
        try:
            # 将 price 和 deposit进行数据类型转换因为获取的这两个数据是字符串类型, 数据库中是int
            # 数据里这两个单位是分
            price = int(float(price) * 100)
            deposit = int(float(deposit) * 100)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"errno": RET.PARAMERR, "errmsg": "参数错误"})

        # 因为添加数据的时候 对同一个对象会操作两次 使用事件
        with transaction.atomic():
            save_id = transaction.savepoint()
            # 保存数据
            try:
                house = House.objects.create(user=user,title=title,price=price,area_id=area_id,address=address,room_count=room_count,
                              acreage=acreage,unit=unit,capacity=capacity,beds=beds,deposit=deposit,min_days=min_days,max_days=max_days)
            except DatabaseError as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({"errno": RET.DBERR, "errmsg": "数据库保存失败"})

            # 添加设施  房间表和设施表是多对多的关系  facility_ids 中保存的是设施的id
            try:
                if facility_ids:
                    # facility_ids 不为空 则查找对应的设施名字 in表示范围查询, 是否包含在范围内
                    facilitys = Facility.objects.filter(id__in=facility_ids)
                    for facility in facilitys:
                        house.facility.add(facility)
            except DatabaseError as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({"errno": RET.DBERR, "errmsg": "数据库保存失败"})
            transaction.savepoint_commit(save_id)
        return http.JsonResponse({"errno": RET.OK, "errmsg": "发布成功","data":{"house_id":house.id}})

# 上传房源图片
class ReleaseHouseImageView(View):

    @method_decorator(login_required)
    def post(self,request,house_id):
        # 获取数据
        image = request.FILES.get('house_image')
        if not image:
            # 若是没有上传图片
            return http.JsonResponse({"errno": RET.PARAMERR, "errmsg": "参数错误"})
        # 验证上传的文件是否是图片
        if not  image_file(image):
            return http.JsonResponse({"errno": RET.PARAMERR, "errmsg": "参数错误"})

        # 验证房屋是否存在
        try:
            house = House.objects.get(id=house_id)
        except DatabaseError as e:
            logger.error(e)
            return http.JsonResponse({"errno": RET.NODATA, "errmsg": "该房间不存在"})

        file_data = image.read()
        # 验证通过 上传文件到七牛云
        try:
            key = storage(file_data)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"errno": RET.THIRDERR, "errmsg": "上传图片失败"})

        # 保存图片到数据库 需要操作的数据库有 house 保存房屋的 主图片 以及 房屋图片 因为操作两个数据库所以使用 事务
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                # 判断 house中的 主图片是否有 没有的话,则添加
                if not house.index_image_url:
                    house.index_image_url = key
                    house.save()
                house_image = HouseImage(house=house,url=key)
                house_image.save()
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({"errno": RET.THIRDERR, "errmsg": "上传图片失败"})
            else:
                transaction.savepoint_commit(save_id)

        data = {"url":settings.QINIU_URL+key}
        return http.JsonResponse({"errno":RET.OK,"errmsg":"图片上传成功","data":data})

