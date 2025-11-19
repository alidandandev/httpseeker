#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pyotp
import datetime
import operator
import random


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


def generate_account() -> str:
    """
    生成账号，格式为autotester+6位随机数（例如：autotester123456）
    :return: 生成的账号字符串
    """
    random_suffix = random.randint(100000, 999999)
    return f"autotester{random_suffix}"


def generate_five_digit_number() -> int:
    """
    生成五位数随机数（范围10000-99999，确保是5位整数）
    :return: 五位数的随机整数（例如：12345）
    """
    return random.randint(10000, 99999)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pyotp
import datetime
import operator
import random


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


def get_login_google_auth_code(secret_key: str = "VSXYK3DI7ZTQCV4C") -> str:
    """
    获取谷歌验证码（TOTP）
    :param secret_key: 谷歌验证器密钥，默认为配置的密钥
    :return: 6位数字验证码
    """
    return pyotp.TOTP(secret_key).now()


def get_action_google_auth_code(secret_key: str = "NUEKYKJUW72ZQKC6") -> str:
    """
    获取谷歌验证码（TOTP）
    :param secret_key: 谷歌验证器密钥，默认为配置的密钥
    :return: 6位数字验证码
    """
    return pyotp.TOTP(secret_key).now()


def generate_account() -> str:
    """
    生成账号，格式为autotester+6位随机数（例如：autotester123456）
    :return: 生成的账号字符串
    """
    random_suffix = random.randint(100000, 999999)
    return f"autotester{random_suffix}"


def generate_five_digit_number() -> int:
    """生成五位数随机数，仅第一次调用时生成，后续返回静态变量值"""
    if not hasattr(generate_five_digit_number, "_cached_value"):
        print("生成随机数（仅执行一次）")
        generate_five_digit_number._cached_value = random.randint(10000, 99999)
    return generate_five_digit_number._cached_value


def generate_today_time() -> str:
    """
    生成今天的时间，格式为“年-月-日+时:分:秒”（例如：2025-11-09+23:59:59）
    时间部分固定为23:59:59
    :return: 符合格式的今天时间字符串
    """
    today_date = datetime.date.today().strftime("%Y-%m-%d")
    return f"{today_date}+23:59:59"


def generate_time_90_days_ago() -> str:
    """
    生成90天前的时间，格式为“年-月-日+时:分:秒”（例如：2025-08-10+00:00:00）
    时间部分固定为00:00:00
    :return: 符合格式的90天前时间字符串
    """
    ninety_days_ago = datetime.date.today() - datetime.timedelta(days=90)
    return f"{ninety_days_ago.strftime('%Y-%m-%d')}+00:00:00"


def generate_today_start_time() -> str:
    """
    生成今天的开始时间，格式为“年-月-日+时:分:秒”（例如：2025-11-09+00:00:00）
    时间部分固定为00:00:00
    :return: 符合格式的今天开始时间字符串
    """
    today_date = datetime.date.today().strftime("%Y-%m-%d")
    return f"{today_date}+00:00:00"


def get_invitation_code() -> int:
    """
    生成六位数随机数（范围100000-999999，确保是6位整数）
    :return: 六位数的随机整数（例如：123456）
    """
    return random.randint(100000, 999999)


