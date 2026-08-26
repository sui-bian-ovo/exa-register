#!/usr/bin/python3.12
# -*- coding: utf-8 -*-
#
# @Time  : 2026/8/24 14:30
# @File  : bit.py

import time
import uuid

import requests
from loguru import logger


class BitPlus(object):
    URL = "http://127.0.0.1:54345"
    DISPLAYS = None

    def __init__(self, browser_id):
        self.browser_id = browser_id
        self.base_json = {"id": browser_id}
        self.open_data = None
        self.browser_detail = None

    def init_browser_detail(self):
        self.browser_detail = requests.post(
            f"{self.URL}/browser/detail",
            json=self.base_json,
        ).json()['data']

    @classmethod
    def create_profile(
            cls,
            proxy_config: dict = None,
    ) -> tuple[str, dict]:
        """创建浏览器窗口配置

        BitBrowser API: POST /browser/update
        创建窗口时 browserFingerPrint 必传，传 {} 则随机生成指纹。

        Returns:
            profile_id (浏览器窗口 ID)
        """
        body = {
            "name": f'{uuid.uuid4()}',
            "proxyMethod": 2,
            "proxyType": "noproxy",
            "browserFingerPrint": {
                'isIpCreateLanguage': False,
                'isIpCreateDisplayLanguage': False,
                'country': 'CN',
                'languages': 'zh-CN',
                'displayLanguages': 'zh-CN',
                'credentialsEnableService': True,
                'ignoreHttpsErrors': True,
            },
            'credentialsEnableService': True,

        }
        if proxy_config:
            body.update(proxy_config)

        data = requests.post(f"{cls.URL}/browser/update", json=body).json()
        profile = data['data']
        profile_id = data['data'].get("id", "")
        logger.info(f"Profile 已创建: {profile_id}")
        return profile_id, profile

    def open(self):
        logger.info(f'打开浏览器 | browser_id={self.browser_id}')
        for i in range(1, 4):
            res = requests.post(
                f"{self.URL}/browser/open",
                json=self.base_json,
            ).json()
            if res['success']:
                self.open_data = res['data']
                self.init_browser_detail()
                break
            else:
                logger.warning(f'打开浏览器失败【{i}/3】 | msg={res["msg"]}')
                time.sleep(6 ** i)
        else:
            raise Exception('打不开浏览器')

    def close(self):
        res = requests.post(
            f"{self.URL}/browser/close",
            json=self.base_json,
        )
        # logger.debug(f'关闭浏览器 | res={res}')
        time.sleep(5)

    def delete(self):
        res = requests.post(
            f"{self.URL}/browser/delete",
            json=self.base_json,
        )
        # logger.debug(f'删除浏览器 | res={res}')
