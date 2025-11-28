#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpseeker.enums import StrEnum


class AuthType(StrEnum):
    TOKEN = 'bearer_token'
    TOKEN_CUSTOM = 'bearer_token_custom'
    COOKIE = 'header_cookie'
    TK = 'tk'  # 自定义token认证，请求头字段名为tk
    AUTHORIZATION = 'authorization'  # Authorization头认证，不带Bearer前缀
