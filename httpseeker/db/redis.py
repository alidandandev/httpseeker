#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

from redis import AuthenticationError, Redis

from httpseeker.common.log import log
from httpseeker.core.get_conf import httpseeker_config


class RedisDB:
    def __init__(self) -> None:
        self._client = None
        self._enabled = False
        self.prefix = 'httpseeker'
        self.token_prefix = f'{self.prefix}:token'
        self.cookie_prefix = f'{self.prefix}:cookie'
        self.case_data_prefix = f'{self.prefix}:case_data'
        self.case_id_file_prefix = f'{self.prefix}:case_id_file'

        # 只有配置了有效的 Redis 连接信息才初始化客户端
        if all([
            httpseeker_config.REDIS_HOST,
            httpseeker_config.REDIS_PORT is not None,
        ]):
            try:
                self._client = Redis(
                    host=httpseeker_config.REDIS_HOST,
                    port=httpseeker_config.REDIS_PORT,
                    password=httpseeker_config.REDIS_PASSWORD,
                    db=httpseeker_config.REDIS_DATABASE,
                    socket_timeout=httpseeker_config.REDIS_TIMEOUT,
                    decode_responses=True,  # 转码 utf-8
                )
                self._enabled = True
            except Exception as e:
                log.warning(f'Redis 连接初始化失败，Redis 功能将不可用: {e}')
                self._enabled = False
        else:
            log.info('Redis 配置未完整提供，跳过 Redis 连接初始化')

    def init(self) -> None:
        if not self._enabled or not self._client:
            log.info('Redis 未启用，跳过连接测试')
            return
        try:
            self._client.ping()
        except TimeoutError:
            log.error('数据库 redis 连接超时')
        except AuthenticationError:
            log.error('数据库 redis 授权认证错误')
        except Exception as e:
            log.error(f'数据库 redis 连接异常: {e}')
        else:
            log.info('数据库 redis 连接成功')

    def get(self, name: Any, logging: bool = True) -> Any:
        """
        获取 redis 数据

        :param name:
        :param logging:
        :return:
        """
        if not self._enabled or not self._client:
            return None
        data = self._client.get(name)
        if not data:
            if logging:
                log.warning(f'获取 redis 数据 {name} 失败, 此数据不存在')
        return data

    def get_prefix(self, prefix: str) -> list:
        """
        获取 redis 符合前缀的数据

        :param prefix: key 前缀
        :return:
        """
        if not self._enabled or not self._client:
            return []
        data = []
        for key in self._client.scan_iter(match=f'{prefix}*'):
            value = self._client.get(key)
            if value:
                data.append(value)
        return data

    def set(self, key: Any, value: Any, **kwargs) -> None:
        """
        设置 redis 数据

        :param key:
        :param value:
        :param kwargs:
        :return:
        """
        if not self._enabled or not self._client:
            return
        self._client.set(key, value, **kwargs)

    def exists(self, key: Any) -> bool:
        """
        检查 redis key 是否存在

        :param key:
        :return:
        """
        if not self._enabled or not self._client:
            return False
        return bool(self._client.exists(key))

    def delete(self, *keys: Any) -> None:
        """
        删除 redis 数据

        :param keys:
        :return:
        """
        if not self._enabled or not self._client:
            return
        self._client.delete(*keys)

    def rset(self, key: Any, value: Any, **kwargs) -> None:
        """
        重置设置 redis 数据

        :param key:
        :param value:
        :param kwargs:
        :return:
        """
        if not self._enabled or not self._client:
            return
        if self.exists(key):
            self.delete(key)
        self.set(key, value, **kwargs)

    def delete_prefix(self, prefix: str, exclude: str | None = None) -> None:
        """
        删除 redis 符合前缀的数据

        :param prefix: key 前缀
        :param exclude: 排除的前缀
        :return:
        """
        if not self._enabled or not self._client:
            return
        for key in self._client.scan_iter(match=f'{prefix}*'):
            if not exclude:
                self.delete(key)
            else:
                if not key.startswith(exclude):
                    self.delete(key)

    @property
    def is_enabled(self) -> bool:
        """检查 Redis 是否已启用"""
        return self._enabled


redis_client = RedisDB()
