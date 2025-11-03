#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pyotp
import datetime
import operator

from faker import Faker

faker = Faker(locale='zh_CN')


def current_time() -> datetime.datetime:
    """
    :return: 获取当前时间
    """
    return datetime.datetime.now()


def random_phone() -> str:
    """
    :return: 随机手机号
    """
    return faker.phone_number()


def sum_a_b(a: int, b: int) -> int:
    return operator.add(a, b)


def get_google_auth_code(secret_key: str = "R5C54O5CX6LQCZA6") -> str:
    """
    获取谷歌验证码（TOTP）
    :param secret_key: 谷歌验证器密钥，默认为配置的密钥
    :return: 6位数字验证码
    """
    return pyotp.TOTP(secret_key).now()
