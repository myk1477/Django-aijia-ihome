# -*- coding:utf-8 -*-

# import ssl
# ssl._create_default_https_context =ssl._create_stdlib_context # 解决Mac开发环境下，网络错误的问题

from verifications.libs.yuntongxun.CCPRestSDK import REST

# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
_accountSid = '8aaf07086010a0eb01602ec373bb0c35'

# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_accountToken = 'aa075805e30e43d18d2fcfa4816a76fc'

# 请使用管理控制台首页的APPID或自己创建应用的APPID
_appId = '8a216da86010e69001602ee1defa0cbc'

# 说明：请求地址，生产环境配置成app.cloopen.com
_serverIP = 'sandboxapp.cloopen.com'

# 说明：请求端口 ，生产环境为8883
_serverPort = "8883"

# 说明：REST API版本号保持不变
_softVersion = '2013-12-26'

# 云通讯官方提供的发送短信代码实例
# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id
# def sendTemplateSMS(to, datas, tempId):
#     # 初始化REST SDK
#     rest = REST(_serverIP, _serverPort, _softVersion)
#     rest.setAccount(_accountSid, _accountToken)
#     rest.setAppId(_appId)
#
#     result = rest.sendTemplateSMS(to, datas, tempId)
#     print(result)


class CCP(object):

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, "_instants"):
            cls._instants = super(CCP, cls).__new__(cls, *args, **kwargs)
            # 单例在使用完会销毁，那么当我们初始化发送短信验证的的对象后，也需要销毁
            cls._instants.rest = REST(_serverIP, _serverPort, _softVersion)
            cls._instants.rest.setAccount(_accountSid, _accountToken)
            cls._instants.rest.setAppId(_appId)

        return cls._instants

    def send_sms_code(self, to, datas, temp_id):
        result = self.rest.sendTemplateSMS(to, datas, temp_id)

        if result.get("statusCode") == "000000":
            return 0
        else:
            return -1


if __name__ == '__main__':
    # 注意： 测试的短信模板编号为1
    # sendTemplateSMS('18511551140', ['123456', 5], 1)
    CCP().send_sms_code('18511551140', ['123456', 5], 1)
