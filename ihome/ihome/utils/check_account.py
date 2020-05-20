from django.contrib.auth.backends import ModelBackend

from users.models import User


def get_user_by_account(account):
    """
    根据account查询用户
    :param account: 用户名或者手机号
    :return: user
    """
    try:
        user = User.objects.get(username=account)
    except User.DoesNotExist:
        try:
            user = User.objects.get(mobile=account)
        except User.DoesNotExist:
            return None

    return user


class UsernameMobileAuthBackend(ModelBackend):
    """自定义用户认证后端"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        # 校验user是否存在并校验密码是否正确
        if user and user.check_password(password):
            return user