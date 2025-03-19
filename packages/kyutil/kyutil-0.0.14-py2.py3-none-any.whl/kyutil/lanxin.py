# -*- coding: UTF-8 -*-
import base64
import hashlib
import hmac
import time
from urllib.parse import urlencode
from urllib.parse import urljoin

from .http_util import send_request

Lx_config = {
    "appid": "15868416-11386880",
    "app_secret": "**",
    # 平台接入地址
    "api_url": "https://apigw-cec.cec.com.cn",
    "auth_url": "https://passport-cec.cec.com.cn",
    # 获取app_token地址
    "app_token_url": "/v1/apptoken/create",
    # 获取user_token地址
    "user_token_url": "/v1/usertoken/create",
    # 获取user_info
    "user_info_url": "/v1/users/fetch",
    # 获取人员唯一标识地址
    "user_id_url": "/v2/staffs/id_mapping/fetch",
    # 发送消息地址
    "send_msg": "/v1/messages/create",
    # 根据名称模糊搜索
    "search_user": "/v2/staffs/search"
}


def join_param(url: str, params: dict):
    # 对参数进行编码
    encoded_params = urlencode(params)

    # 拼接URL和参数
    url_with_params = url + '?' + encoded_params
    return url_with_params


def get_app_token(appid=Lx_config.get("appid"), secret=Lx_config.get("app_secret"), proxy=None):
    params = {
        "grant_type": "client_credential",
        "appid": appid,
        "secret": secret
    }
    url = join_param(urljoin(Lx_config.get("api_url"), Lx_config.get("app_token_url")), params)
    jd = send_request(url, verify=False, proxies=proxy, timeout=7).json()
    if jd.get("errCode") == 0:
        data = jd.get("data")
        app_token = data.get("app_token")
        return app_token
    else:
        err_msg = jd.get("errMsg")
        raise RuntimeError(f"获取appToken失败,errCode={jd.get('errCode')},errMsg={err_msg}")


# 模糊搜索人员信息 建议使用中文名
def get_user_info(app_token: str, username: str, proxy=None):
    user_param = {'app_token': app_token,
                  'user_id': '15868416-5Wuq3fjlKR7WHLApLP6CzMjMnIeD00e',
                  'page': 1,
                  'page_size': 10}
    url = join_param(urljoin(Lx_config.get("api_url"), Lx_config.get("search_user")), user_param)
    body = {
        "keyword": username,
        "recursive": True,
        "searchScope": {
            "sectorIds": [
                "15868416-alujjum36KmGhyJXyerIezAeJHP8v1WD"
            ]
        }
    }
    jd = send_request(url, method="post", json=body, proxies=proxy, timeout=7).json()
    if jd.get("errCode") == 0:
        data = jd.get("data")
        staff_info_list = data.get("staffInfo")
        staff_id = staff_info_list[0].get("staffId", "")
        if staff_id == "":
            raise RuntimeError("获取staff_id失败")
        return staff_id
    else:
        err_msg = jd.get("errMsg")
        raise RuntimeError(f"获取人员id失败,errCode={jd.get('errCode')},,errMsg={err_msg}")


def send_message_text(app_token: str, staff_id_list: list, message: str, proxy=None):
    param = {'app_token': app_token}
    url = join_param(urljoin(Lx_config.get("api_url"), Lx_config.get("send_msg")), param)
    body = {
        "userIdList": staff_id_list,
        "msgType": "text",
        "msgData": {
            "text": {
                "content": message,
                "reminder": {
                }
            }
        }
    }
    response = send_request(url, json=body, proxies=proxy, method="post", timeout=7).json()
    if response.get("errCode") != 0:
        err_msg = response.get("errMsg")
        raise RuntimeError(f"发送信息失败,errCode={response.get('errCode')},errMsg={err_msg}")
    return response


class LanXin:
    """蓝信群"""

    def __init__(self, secret, url):
        self.secret = secret
        self.url = url

    def sendmsg(self, msg, proxy=None):
        timestamp = int(round(time.time()))
        string_to_sign = '{}@{}'.format(timestamp, self.secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        d = {
            "timestamp": str(timestamp),
            "sign": sign,
            "msgType": "text",
            "msgData": {
                "text": {
                    "content": msg,
                }
            }
        }
        headers = {
            "Content-Type": "application/json"
        }
        try:
            return send_request(self.url, json=d, headers=headers, proxies=proxy, method="post", timeout=7)
        except ConnectionError as e:
            print(f"无法发送蓝信消息，错误：{e}")
            return None

    def send_articles(self, msg, proxy=None):
        timestamp = int(round(time.time()))
        string_to_sign = '{}@{}'.format(timestamp, self.secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        d = {
            "timestamp": str(timestamp),
            "sign": sign,
            "msgType": "appArticles",
            "msgData": {
                "appArticles": msg
            }
        }
        headers = {
            "Content-Type": "application/json"
        }
        return send_request(self.url, json=d, headers=headers, proxies=proxy, method="post", timeout=7)
