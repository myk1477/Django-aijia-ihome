from django.db.models import Q

from order.models import Order
from utils.model import BaseModel
from django.db import models
from django.conf import settings


class Area(BaseModel):
    """城区"""

    name = models.CharField(max_length=32, null=False, verbose_name="区域名字")

    class Meta:
        db_table = "tb_area"

    def to_dict(self):
        """将对象转换为字典数据"""
        area_dict = {
            "aid": self.pk,
            "aname": self.name
        }
        return area_dict


class Facility(BaseModel):
    """设施信息"""

    name = models.CharField(max_length=32, null=False, verbose_name="设施名字")

    class Meta:
        db_table = "tb_facility"


class House(BaseModel):
    """房屋信息"""
    user = models.ForeignKey("users.User", related_name='houses', on_delete=models.CASCADE, verbose_name='房屋主人的用户编号')
    area = models.ForeignKey("Area", null=False, on_delete=models.CASCADE, verbose_name="归属地的区域编号")
    title = models.CharField(max_length=64, null=False, verbose_name="标题")
    price = models.IntegerField(default=0)  # 单价，单位：分
    address = models.CharField(max_length=512, default="")  # 地址
    room_count = models.IntegerField(default=1)  # 房间数目
    acreage = models.IntegerField(default=0)  # 房屋面积
    unit = models.CharField(max_length=32, default="")  # 房屋单元， 如几室几厅
    capacity = models.IntegerField(default=1)  # 房屋容纳的人数
    beds = models.CharField(max_length=64, default="")  # 房屋床铺的配置
    deposit = models.IntegerField(default=0)  # 房屋押金
    min_days = models.IntegerField(default=1)  # 最少入住天数
    max_days = models.IntegerField(default=0)  # 最多入住天数，0表示不限制
    order_count = models.IntegerField(default=0)  # 预订完成的该房屋的订单数
    index_image_url = models.CharField(max_length=256, default="")  # 房屋主图片的路径
    facility = models.ManyToManyField("Facility", verbose_name="和设施表之间多对多关系")

    class Meta:
        db_table = "tb_house"

    def to_basic_dict(self):
        """将基本信息转换为字典数据"""
        house_dict = {
            "house_id": self.pk,
            "title": self.title,
            "price": self.price,
            "area_name": self.area.name,
            "img_url": settings.QINIU_URL + self.index_image_url if self.index_image_url else "",
            "room_count": self.room_count,
            "order_count": self.order_count,
            "address": self.address,
            "user_avatar": settings.QINIU_URL + self.user.avatar.name if self.user.avatar.name else "",
            "ctime": self.create_time.strftime("%Y-%m-%d")
        }
        return house_dict

    def to_full_dict(self):
        """将详细信息转换为字典数据"""
        house_dict = {
            "hid": self.pk,
            "user_id": self.user.id,
            "user_name": self.user.username,
            "user_avatar": settings.QINIU_URL + self.user.avatar.name if self.user.avatar.name else "",
            "title": self.title,
            "price": self.price,
            "address": self.address,
            "room_count": self.room_count,
            "acreage": self.acreage,
            "unit": self.unit,
            "capacity": self.capacity,
            "beds": self.beds,
            "deposit": self.deposit,
            "min_days": self.min_days,
            "max_days": self.max_days,
        }

        # 房屋图片
        img_urls = []
        for image in self.houseimage_set.all():
            img_urls.append(settings.QINIU_URL + image.url)
        house_dict["img_urls"] = img_urls

        # 房屋设施
        facilities = []
        for facility in self.facility.all():
            facilities.append(facility.id)
        house_dict["facilities"] = facilities

        # 评论信息
        comments = []
        orders = Order.objects.filter(house=self, status=Order.ORDER_STATUS["COMPLETE"], comment__isnull=False).order_by("-update_time")[0:30]
        for order in orders:
            comment = {
                "comment": order.comment,  # 评论的内容
                "user_name": order.user.username if order.user.username != order.user.mobile else "匿名用户",  # 发表评论的用户
                "ctime": order.update_time.strftime("%Y-%m-%d %H:%M:%S")  # 评价的时间
            }
            comments.append(comment)
        house_dict["comments"] = comments
        return house_dict


class HouseImage(BaseModel):
    """
    房屋图片表
    """
    house = models.ForeignKey("House", on_delete=models.CASCADE)  # 房屋编号
    url = models.CharField(max_length=256, null=False)  # 图片的路径

    class Meta:
        db_table = "tb_house_image"