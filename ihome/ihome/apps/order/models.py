from django.conf import settings
from django.db import models

# Create your models here.
from utils.model import BaseModel


class Order(BaseModel):
    """订单"""
    ORDER_STATUS = {
        "WAIT_ACCEPT": 0,  # 待接单,
        "WAIT_PAYMENT": 1,  # 待支付
        "PAID": 2,  # 已支付
        "WAIT_COMMENT": 3,  # 待评价
        "COMPLETE": 4,  # 已完成
        "CANCELED": 5,  # 已取消
        "REJECTED": 6  # 已拒单
    }

    ORDER_STATUS_ENUM = {
        0: "WAIT_ACCEPT",  # 待接单,
        1: "WAIT_PAYMENT",  # 待支付
        2: "PAID",  # 已支付
        3: "WAIT_COMMENT",  # 待评价
        4: "COMPLETE",  # 已完成
        5: "CANCELED",  # 已取消
        6: "REJECTED"  # 已拒单
    }
    ORDER_STATUS_CHOICES = (
            (0 ,"WAIT_ACCEPT"),  # 待接单,
            (1, "WAIT_PAYMENT"),  # 待支付
            (2, "PAID"),  # 已支付
            (3, "WAIT_COMMENT"),  # 待评价
            (4, "COMPLETE"),  # 已完成
            (5, "CANCELED"),  # 已取消
            (6, "REJECTED")  # 已拒单
        )

    user = models.ForeignKey("users.User", related_name="orders", on_delete=models.CASCADE, verbose_name="下订单的用户编号")
    house = models.ForeignKey("homes.House", on_delete=models.CASCADE, verbose_name="预订的房间编号")
    begin_date = models.DateField(null=False, verbose_name="预订的起始时间")
    end_date = models.DateField(null=False, verbose_name="结束时间")
    days = models.IntegerField(null=False, verbose_name="预订的总天数")
    house_price = models.IntegerField(null=False, verbose_name="房屋单价")
    amount = models.IntegerField(null=False, verbose_name="订单总金额")
    status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=0, db_index=True, verbose_name="订单状态")
    comment = models.TextField(null=True, verbose_name="订单的评论信息或者拒单原因")

    class Meta:
        db_table = "tb_order"

    def to_dict(self):
        """将订单信息转换为字典数据"""
        order_dict = {
            "order_id": self.pk,
            "title": self.house.title,
            "img_url": settings.QINIU_URL + self.house.index_image_url if self.house.index_image_url else "",
            "start_date": self.begin_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "ctime": self.create_time.strftime("%Y-%m-%d %H:%M"),
            "days": self.days,
            "amount": self.amount,
            "status": Order.ORDER_STATUS_ENUM[self.status],
            "comment": self.comment if self.comment else ""
        }
        return order_dict
