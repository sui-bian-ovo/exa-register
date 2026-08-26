#!/usr/bin/python3.12
# -*- coding: utf-8 -*-
#
# @Time  : 2026/8/20 16:36
# @File  : register.py

import re
from datetime import datetime
import time
from pathlib import Path
from threading import Lock

import yaml
from DrissionPage import Chromium, ChromiumOptions
from loguru import logger

from bit import BitPlus
from mails import get_email_provider

with open('cfg.yaml', 'r', encoding='utf-8') as file:
    cfg = yaml.load(file, Loader=yaml.FullLoader)
write_lock = Lock()

co = ChromiumOptions().auto_port()
co.incognito()  # 匿名模式
email_provider = get_email_provider()


class Register(object):

    def __init__(self):

        self.api_key = None
        self.send_datetime = None
        proxy_config = dict()
        if cfg['use_proxy']:
            proxy_config = {
                'proxyMethod': 3,
                'proxyType': 'http',
                'dynamicIpUrl': f'http://127.0.0.1:{cfg["proxy_backend_port"]}/get-proxy',
            }
        profile_id, profile = BitPlus.create_profile(proxy_config=proxy_config)
        self.bit = BitPlus(profile_id)
        self.bit.open()
        browser = Chromium(self.bit.open_data['http'])
        self.tab = browser.latest_tab

        self.email = email_provider.get_email()

    def get_api_key(self):
        for text in ['Cursor', 'Python', 'Web', 'Generate']:
            self.tab(f'tx:{text}').click()

        start_time = time.time()
        idx = 0
        while True:
            idx += 1
            logger.debug(f'开始第 {idx} 次等待校 api key 加载...')
            if time.time() - start_time > cfg['timeout']:
                raise TimeoutError('待校 api key 加载超时')
            try:
                self.tab('code').next().click()
                self.api_key = self.tab('code').text
                return
            except:
                pass

    def verify_opt(self):
        code = email_provider.get_mail_data(
            self.email, lambda x: re.search(
                r'>([0-9A-Za-z]{6})<',
                x,
                re.MULTILINE
            ).group(1),
            self.send_datetime
        )
        logger.info(f'收到验证码 | code={code}')
        self.tab('@type=submit').prev().input(code)
        self.tab.wait(0.5)
        self.tab('@type=submit').click()
        self.tab.wait(10)

        start_time = time.time()
        idx = 0
        while True:
            idx += 1
            logger.debug(f'开始第 {idx} 次等待校验注册...')
            for text in [
                'Too many accounts have been created from this network.',
                'An error occurred during sign in',
            ]:
                if text in self.tab.html:
                    raise Exception(text)
            if time.time() - start_time > cfg['timeout']:
                raise TimeoutError('等待校验注册超时')
            if self.tab('tx:Cursor', timeout=0):
                logger.info('通过校验注册')
                break
            self.tab.wait(1)

    def get_cf_texts(self) -> list[str]:
        try:
            texts = self.tab.ele(
                'tx=Sign in with SSO', timeout=5
            ).prev(timeout=5).child(timeout=5).child(timeout=5).sr.ele(
                './/iframe',
                timeout=5
            )('.//body', timeout=5).sr.eles('div', timeout=5).filter.displayed().get.texts()
            texts = [text for text in texts if text]
        except:
            logger.warning('获取 cf 盾 texts 失败')
            texts = list()
        return texts

    def pass_cf(self):
        start = time.time()
        idx = 0
        while True:
            idx += 1
            logger.debug(f'开始第 {idx} 次通过 cf...')
            texts = self.get_cf_texts()
            logger.debug(f'cf 盾 texts | texts={texts}')
            if '成功！' in texts:
                logger.info('已通过 cf 盾')
                return
            if time.time() - start > cfg['timeout']:
                raise TimeoutError('通过 cf 盾超时')
            try:
                ele = self.tab.ele('tx=Sign in with SSO', timeout=5).prev()
                if ele:
                    width, height = ele.rect.size
                    self.tab.actions.move_to(ele, offset_x=int(width / 20), offset_y=int(height / 2)).click()
                    self.tab.wait(3)
            except Exception as e:
                logger.warning(f'尝试通过 cf 盾报错 开始下一次尝试 | e={e}')

    def run(self):
        self.tab.get('https://auth.exa.ai/?callbackUrl=https%3A%2F%2Fdashboard.exa.ai%2F')
        self.tab.wait.doc_loaded()
        self.pass_cf()

        self.send_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.tab('@type=email').input(self.email)
        self.tab.wait(0.5)
        self.tab('@type=submit').click()
        self.tab.wait(5)

        self.verify_opt()
        self.get_api_key()

        with write_lock:
            Path('data.txt').open('a', encoding='utf-8').write(
                f"{self.email}----{self.api_key}\n"
            )
        logger.success('注册成功')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.bit.close()
        except:
            logger.warning('关闭浏览器失败')
        try:
            self.bit.delete()
        except:
            logger.warning('删除浏览器失败')


if __name__ == '__main__':
    with Register() as register:
        register.run()
