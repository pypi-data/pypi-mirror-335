"""
快手官方开放接口

快手官方文档地址：https://open.kuaishou.com/platform/openApi

注：上传文件需要 requests-toolbelt
"""

import os
import json
import time
import hashlib
import random
from pathlib import Path
from pprint import pprint as pp

import requests

from requests import Response
from requests_toolbelt import MultipartEncoder
from urllib.parse import urlparse

from .utils import need_login, BaseClient
from .exception import LoginError, NeedAccessTokenException

HEADERS_JSON = {
    "Content-Type": "application/json",  # application/json;charset=UTF-8
    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
}

HEADERS_X_WWW_FORM_URLENCODED = {
    "Content-Type": "application/x-www-form-urlencoded",
}


class KuaiShou(BaseClient):

    def __init__(self, client_key, client_secret, base_url='https://open.kuaishou.com', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_key = client_key  # 应用唯一标识
        self.client_secret = client_secret  # 应用唯一标识对应的密钥
        self.base_url = base_url
        self.set_headers(HEADERS_JSON)
        self.data = {}
        self._access_token = None
        self._open_id = None

    def set_access_token(self, access_token, open_id):
        """
        设置用户授权
        """
        headers = {
            "Content-Type": "application/json",
            "access-token": access_token,
        }
        self.set_headers(headers)
        # 我们获取消息数量，检查是否已经登录成功

        self._access_token = access_token
        self._open_id = open_id

    def need_access_token(self):
        """
        检查是否已登录，我们还是只简单检查有没有 access_token
        """
        # self.get_count_message()
        if self._access_token is None:
            raise NeedAccessTokenException()

    def get_response_data(self, resp):
        """
        解析接口返回的数据
        """
        try:
            self.data = resp.json()
        except Exception as e:
            return {
                "data": {
                    "description": f"转换json数据失败：{e}",
                    "error_code": 88888888,
                }
            }

        # 我们不检查信息是否错误，在获取信息的时候在检查
        # if self.data['data'].get('error_code', None) != 0:
        #     raise ValueError(f'{self.data}')

        return self.data
