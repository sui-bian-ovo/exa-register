#!/usr/bin/python3.12
# -*- coding: utf-8 -*-
#
# @Time  : 2026/8/20 16:48
# @File  : email_provider.py

from abc import abstractmethod, ABC
from typing import Any, Callable


class EmailProvider(ABC):

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def get_email(self) -> str:
        pass

    @abstractmethod
    def get_mail(self, query_data: Any, send_datetime: str = '1900-01-01 01:01:01', timeout=30):
        pass

    def get_mail_data(
            self, query_data: Any, call: Callable,
            send_datetime: str = '1900-01-01 01:01:01',
            timeout=30
    ) -> str:
        raise NotImplementedError(f'{self.provider_name} 没有实现 get_mail_data')
