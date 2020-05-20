import logging

from django.http import HttpResponse
from qiniu import Auth, put_data

# 需要填写你的 Access Key 和 Secret Key
# access_key = 'n1gKo9iDzko8yrck9Zw-XyJochVHsnBWPWlbkpju'
# secret_key = 'SRCV6wb1By71OnM0VHvcHbl_M3R8GmpJ_LRmWCCU'
# 我自己的七牛云
access_key = 'OzD5YEUi0AfnvdfVbrLXlSdWbqAbkMKsU7hbJc6b'
secret_key = 'Vc3izdYI-rUQMcHjmEDBYu7McvNjWANlRKGq1aHb'

# 要上传的空间
# bucket_name = 'djangoihome'
bucket_name = 'django-ihome'


def storage(data):
    """七牛云存储上传文件接口"""
    if not data:
        return None
    try:
        # 构建鉴权对象
        q = Auth(access_key, secret_key)

        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name)

        # 上传文件
        ret, info = put_data(token, None, data)

    except Exception as e:
        logging.error(e)
        raise e

    if info and info.status_code != 200:
        raise Exception("上传文件到七牛失败")

    # 返回七牛中保存的图片名，这个图片名也是访问七牛获取图片的路径
    print(ret["key"])
    return ret["key"]


if __name__ == '__main__':
    file_name = input("输入上传的文件")
    with open(file_name, "rb") as f:
        storage(f.read())

#http://q1q7ug61o.bkt.clouddn.com/FsxYqFsxYqPJ-fJtVZZH2LEshL7o9Ivxn
#http://q1q7ug61o.bkt.clouddn.com/FsxYqPJ-fJtVZZH2LEshL7o9Ivxn