#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from functools import lru_cache

import requests

from jsonpath import findall

from httpseeker.common.errors import AuthError, SendRequestError
from httpseeker.common.yaml_handler import read_yaml
from httpseeker.core.path_conf import httpseeker_path
from httpseeker.db.redis import redis_client
from httpseeker.enums.request.auth import AuthType
from httpseeker.utils.enum_control import get_enum_values


class AuthPlugins:
    def __init__(self) -> None:
        self.auth_data = self.get_auth_data()
        self.is_auth = self.auth_data['is_auth']
        self.auth_type = self.auth_data['auth_type']
        self.auth_type_verify()
        self.timeout = self.auth_data[f'{self.auth_type}']['timeout'] or 86400

    @lru_cache
    def get_auth_data(self) -> dict:
        """获取授权数据"""
        auth_data = read_yaml(httpseeker_path.auth_conf_dir, filename='auth.yaml')
        return auth_data

    def auth_type_verify(self) -> None:
        """授权类型检查"""
        _allow_auth_type = get_enum_values(AuthType)
        if self.auth_type not in _allow_auth_type:
            raise AuthError(f'认证类型错误, 允许 {_allow_auth_type} 之一, 请检查认证配置文件')

    def request_auth(self) -> requests.Response:
        try:
            from httpseeker.utils.encryption_filter import EncryptionFilter

            url = self.auth_data[f'{self.auth_type}']['url']
            headers = self.auth_data[f'{self.auth_type}']['headers']

            # 构建请求体（支持不同的字段名）
            auth_config = self.auth_data[f'{self.auth_type}']
            body_data = {}

            # 兼容不同的字段名配置
            if 'account' in auth_config:
                body_data['account'] = auth_config['account']
                body_data['pwd'] = auth_config.get('pwd', '')
                if 'internationalCode' in auth_config:
                    body_data['internationalCode'] = auth_config['internationalCode']
            else:
                body_data['username'] = auth_config.get('username', '')
                body_data['password'] = auth_config.get('password', '')

            # 检查是否需要加密
            encryption_enabled = auth_config.get('encryption_enabled', False)
            if encryption_enabled:
                encryption_key = auth_config.get('encryption_key')
                encryption_filter = EncryptionFilter(
                    encryption_enabled=True,
                    encryption_key=encryption_key
                )
                encrypted_body, extra_headers = encryption_filter.encrypt_request_body(body_data)
                body_data = encrypted_body
                headers.update(extra_headers)

            request_data = {
                'url': url,
                'data': body_data,
                'headers': headers,
                'proxies': {'http': None, 'https': None},
            }
            if 'application/json' in str(headers):
                request_data.update({'json': request_data.pop('data')})

            response = requests.post(**request_data)
            response.raise_for_status()
        except Exception as e:
            raise SendRequestError(f'授权接口请求响应异常: {e}')
        return response

    @property
    def bearer_token(self) -> str:
        cache_bearer_token = redis_client.get(f'{redis_client.token_prefix}:bearer_token', logging=False)
        if cache_bearer_token:
            token = cache_bearer_token
        else:
            res = self.request_auth()
            jp_token = findall(self.auth_data[f'{self.auth_type}']['token_key'], res.json())
            token = jp_token[0]
            if not token:
                raise AuthError('Token 获取失败，请检查登录接口响应或 token 提取表达式')
            redis_client.set(f'{redis_client.token_prefix}:bearer_token', token, ex=self.timeout)
        return token

    @property
    def bearer_token_custom(self) -> str:
        cache_bearer_token_custom = redis_client.get(f'{redis_client.token_prefix}:bearer_token_custom', logging=False)
        if cache_bearer_token_custom:
            token = cache_bearer_token_custom
        else:
            token = self.auth_data[f'{self.auth_type}']['token']
            redis_client.set(f'{redis_client.token_prefix}:bearer_token_custom', token, ex=self.timeout)
        return token

    @property
    def header_cookie(self) -> dict:
        cache_cookie = redis_client.get(f'{redis_client.cookie_prefix}:header_cookie', logging=False)
        if cache_cookie:
            cookies = json.loads(cache_cookie)
        else:
            res = self.request_auth()
            res_cookie = res.cookies
            cookies = {k: v for k, v in res_cookie.items()}
            if not cookies:
                raise AuthError('Cookie 获取失败，请检查登录接口响应')
            redis_client.set(
                f'{redis_client.cookie_prefix}:header_cookie', json.dumps(cookies, ensure_ascii=False), ex=self.timeout
            )
        return cookies

    @property
    def tk(self) -> str:
        """自定义 tk token 认证"""
        cache_tk_token = redis_client.get(f'{redis_client.token_prefix}:tk', logging=False)
        if cache_tk_token:
            token = cache_tk_token
        else:
            from httpseeker.utils.encryption_filter import EncryptionFilter

            res = self.request_auth()
            response_data = res.json()

            # 检查是否需要解密响应
            auth_config = self.auth_data[f'{self.auth_type}']
            encryption_enabled = auth_config.get('encryption_enabled', False)
            if encryption_enabled:
                encryption_key = auth_config.get('encryption_key')
                encryption_filter = EncryptionFilter(
                    encryption_enabled=True,
                    encryption_key=encryption_key
                )
                response_data = encryption_filter.decrypt_response_data(response_data)

            jp_token = findall(self.auth_data[f'{self.auth_type}']['token_key'], response_data)
            token = jp_token[0]
            if not token:
                raise AuthError('TK Token 获取失败，请检查登录接口响应或 token 提取表达式')
            redis_client.set(f'{redis_client.token_prefix}:tk', token, ex=self.timeout)
        return token


auth = AuthPlugins()
