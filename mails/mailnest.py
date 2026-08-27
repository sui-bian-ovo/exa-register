#!/usr/bin/python3.12
# -*- coding: utf-8 -*-
#
# @Time  : 2026/8/20 16:47
# @File  : mailnest.py

import time
from typing import Any, Callable

import requests
import yaml
from loguru import logger
from tenacity import retry, stop_after_attempt, retry_if_exception_type

from mails.email_provider import EmailProvider

BASE_URL = "https://mailnest.top"
with open('cfg.yaml', 'r', encoding='utf-8') as file:
    cfg = yaml.load(file, Loader=yaml.FullLoader)


class MailNestProvider(EmailProvider):
    provider_name = "outlook"

    def __init__(self):
        api_key = cfg['email']['mailnest']['api_key']
        self.headers = {
            "Authorization": f"Bearer {api_key}",
        }
        self.project_code = cfg['email']['mailnest']['project_code']
        assert api_key, '配置文件里面需要 api_key'
        assert self.project_code, '配置文件里面需要 project_code'

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def _req(self, url, json):
        resp = requests.post(
            url,
            json=json,
            headers=self.headers,
        )
        if resp.status_code == 401:
            raise Exception('api key 错误')
        if resp.status_code != 200:
            raise Exception(resp.text)
        resp_json = resp.json()
        if resp_json['code'] != '00000':
            raise Exception(resp_json['msg'])
        return resp_json['data']

    def get_email(self):
        return self._req(
            f"{BASE_URL}/api/v1/email/temporary/buy",
            json={
                "project_code": self.project_code,
                "count": 1,
            },
        )[0]['email']

    def get_mail(self, query_data: Any, send_datetime: str = '1900-01-01 01:01:01', timeout=30):
        start_time = time.time()
        idx = 0
        while True:
            idx += 1
            logger.debug(f'开始第 {idx} 次收件...')
            if time.time() - start_time > timeout:
                raise TimeoutError(f'收件超时 | data={query_data}')
            mails = self._req(
                f"{BASE_URL}/api/v1/email/receive",
                json={
                    "email": query_data,
                },
            )
            if mails and (mails[0]['received_at'] > send_datetime):
                return mails[0]

    def get_mail_data(
            self, query_data: Any, call: Callable,
            send_datetime: str = '1900-01-01 01:01:01',
            timeout=30
    ) -> str:
        mail = self.get_mail(query_data, send_datetime, timeout)
        return call(mail['body'])
