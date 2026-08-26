#!/usr/bin/python3.12
# -*- coding: utf-8 -*-
#
# @Time  : 2026/8/20 16:43
# @File  : __init__.py

import yaml

from .email_provider import EmailProvider
from .mailnest import MailNestProvider

EMAIL_PROVIDERS = {
    'mailnest': MailNestProvider
}

with open('cfg.yaml', 'r', encoding='utf-8') as file:
    cfg = yaml.load(file, Loader=yaml.FullLoader)


def get_email_provider() -> EmailProvider:
    name = cfg['email']['provider_name']
    if name not in EMAIL_PROVIDERS:
        raise ValueError(f'Email provider {name} not supported')
    return EMAIL_PROVIDERS[name]()
