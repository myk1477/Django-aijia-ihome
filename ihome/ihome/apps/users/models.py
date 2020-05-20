from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from django.conf import settings


class User(AbstractUser):

    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    avatar = models.ImageField(null=True, blank=True, verbose_name='用户头像')
    real_name = models.CharField(max_length=32, null=True, verbose_name="真实姓名")
    id_card = models.CharField(max_length=20, null=True, verbose_name="身份证号")

    class Meta:
        db_table = "tb_user"

    def __str__(self):
        return self.username

    def to_basic_dict(self):
        data = {
            "avatar_url": settings.QINIU_URL + self.avatar.name,
            "create_time": datetime.strftime(self.date_joined,'%Y-%m-%d %H:%M:%S'),
            "mobile": self.mobile,
            "name": self.username,
            "user_id": self.id
        }
        return data

    def to_auth_dict(self):
        data = {
            "real_name": self.real_name,
            "id_card": self.id_card
        }
        return data