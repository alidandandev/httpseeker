#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import time

from functools import lru_cache
from pathlib import Path

import requests

from jsonpath import findall

from httpseeker.common.errors import AuthError, SendRequestError
from httpseeker.common.log import log
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
        # 文件缓存目录（当 Redis 未启用时使用）
        self.cache_dir = Path(httpseeker_path.project_dir) / '.auth_cache'
        self.cache_dir.mkdir(exist_ok=True)

    @lru_cache
    def get_auth_data(self) -> dict:
        """获取授权数据"""
        # 检查是否通过环境变量指定了认证配置文件路径
        auth_path = os.environ.get('HTTPSEEKER_AUTH_PATH')
        if auth_path:
            # 使用指定的认证配置文件路径
            auth_file_path = Path(auth_path)
            auth_data = read_yaml(str(auth_file_path.parent), filename=auth_file_path.name)
        else:
            # 使用默认路径
            auth_data = read_yaml(httpseeker_path.auth_conf_dir, filename='like_bofa_h5.yaml')
        return auth_data

    def auth_type_verify(self) -> None:
        """授权类型检查"""
        _allow_auth_type = get_enum_values(AuthType)
        if self.auth_type not in _allow_auth_type:
            raise AuthError(f'认证类型错误, 允许 {_allow_auth_type} 之一, 请检查认证配置文件')

    def _get_file_cache(self, key: str) -> str | None:
        """
        从文件获取缓存的 token

        Args:
            key: 缓存键名

        Returns:
            缓存的 token，如果不存在或过期返回 None
        """
        cache_file = self.cache_dir / f"{key}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 检查是否过期
            if time.time() > cache_data.get('expire_time', 0):
                log.debug(f'文件缓存 {key} 已过期，将重新获取')
                cache_file.unlink(missing_ok=True)
                return None

            return cache_data.get('value')
        except Exception as e:
            log.warning(f'读取文件缓存 {key} 失败: {e}')
            return None

    def _set_file_cache(self, key: str, value: str, expire_seconds: int = None) -> None:
        """
        设置文件缓存

        Args:
            key: 缓存键名
            value: 缓存值
            expire_seconds: 过期时间（秒）
        """
        cache_file = self.cache_dir / f"{key}.json"
        expire_time = time.time() + (expire_seconds if expire_seconds else self.timeout)

        cache_data = {
            'value': value,
            'expire_time': expire_time,
            'created_at': time.time()
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            log.debug(f'✓ Token 已缓存到文件: {cache_file}')
        except Exception as e:
            log.warning(f'写入文件缓存 {key} 失败: {e}')

    def _get_cache(self, key: str) -> str | None:
        """
        智能获取缓存：优先使用 Redis，如果未启用则使用文件缓存

        Args:
            key: 缓存键名

        Returns:
            缓存的值，如果不存在返回 None
        """
        if redis_client.is_enabled:
            return redis_client.get(key, logging=False)
        else:
            return self._get_file_cache(key)

    def _set_cache(self, key: str, value: str, expire_seconds: int = None) -> None:
        """
        智能设置缓存：优先使用 Redis，如果未启用则使用文件缓存

        Args:
            key: 缓存键名
            value: 缓存值
            expire_seconds: 过期时间（秒）
        """
        if redis_client.is_enabled:
            redis_client.set(key, value, ex=expire_seconds if expire_seconds else self.timeout)
        else:
            log.info(f'Redis 未启用，使用文件缓存存储 Token')
            self._set_file_cache(key, value, expire_seconds)

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
        cache_key = f'{redis_client.token_prefix}:bearer_token'
        cache_bearer_token = self._get_cache(cache_key)
        if cache_bearer_token:
            token = cache_bearer_token
            log.debug('✓ 使用缓存的 Bearer Token')
        else:
            log.info('缓存中无 Bearer Token，开始调用登录接口获取...')
            res = self.request_auth()
            jp_token = findall(self.auth_data[f'{self.auth_type}']['token_key'], res.json())
            token = jp_token[0]
            if not token:
                raise AuthError('Token 获取失败，请检查登录接口响应或 token 提取表达式')
            self._set_cache(cache_key, token, self.timeout)
            log.info('✓ Bearer Token 获取成功并已缓存')
        return token

    @property
    def bearer_token_custom(self) -> str:
        cache_key = f'{redis_client.token_prefix}:bearer_token_custom'
        cache_bearer_token_custom = self._get_cache(cache_key)
        if cache_bearer_token_custom:
            token = cache_bearer_token_custom
        else:
            token = self.auth_data[f'{self.auth_type}']['token']
            self._set_cache(cache_key, token, self.timeout)
        return token

    @property
    def header_cookie(self) -> dict:
        cache_key = f'{redis_client.cookie_prefix}:header_cookie'
        cache_cookie = self._get_cache(cache_key)
        if cache_cookie:
            cookies = json.loads(cache_cookie)
            log.debug('✓ 使用缓存的 Cookie')
        else:
            log.info('缓存中无 Cookie，开始调用登录接口获取...')
            res = self.request_auth()
            res_cookie = res.cookies
            cookies = {k: v for k, v in res_cookie.items()}
            if not cookies:
                raise AuthError('Cookie 获取失败，请检查登录接口响应')
            self._set_cache(cache_key, json.dumps(cookies, ensure_ascii=False), self.timeout)
            log.info('✓ Cookie 获取成功并已缓存')
        return cookies

    @property
    def tk(self) -> str:
        """自定义 tk token 认证"""
        cache_key = f'{redis_client.token_prefix}:tk'
        cache_tk_token = self._get_cache(cache_key)
        if cache_tk_token:
            token = cache_tk_token
            log.debug('✓ 使用缓存的 TK Token')
        else:
            from httpseeker.utils.encryption_filter import EncryptionFilter

            log.info('缓存中无 TK Token，开始调用登录接口获取...')
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
            self._set_cache(cache_key, token, self.timeout)
            log.info(f'✓ TK Token 获取成功并已缓存（有效期: {self.timeout}秒）')
        return token


auth = AuthPlugins()
