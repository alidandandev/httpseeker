#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSONPath 提取器
用于从响应中提取数据供后续接口使用
"""
from __future__ import annotations

import json
import re

from typing import Any, Dict, Optional, Union

from jsonpath_ng import parse
from jsonpath_ng.ext import parse as ext_parse
from jsonpath_ng.exceptions import JSONPathError

from httpseeker.common.log import log


class JSONPathExtractor:
    """
    JSONPath 数据提取器
    支持从JSON响应中提取数据并保存为变量供后续使用
    """

    def __init__(self):
        """初始化提取器"""
        self.variables = {}  # 存储提取的变量
        self.response_cache = {}  # 缓存响应数据

    def extract(
        self,
        data: Union[Dict, str],
        path: str,
        variable_name: Optional[str] = None,
        default: Any = None,
        use_extended: bool = True
    ) -> Any:
        """
        从JSON数据中提取值

        Args:
            data: JSON数据（字典或JSON字符串）
            path: JSONPath表达式
            variable_name: 保存到变量的名称（可选）
            default: 找不到时的默认值
            use_extended: 是否使用扩展语法（支持更多功能）

        Returns:
            提取的值（如果是单个值返回值本身，多个值返回列表）

        Examples:
            >>> extractor = JSONPathExtractor()
            >>> data = {"code": 200, "data": {"token": "abc123", "user": {"id": 1}}}
            >>> extractor.extract(data, "$.data.token")  # 返回 "abc123"
            >>> extractor.extract(data, "$.data.user.id", "user_id")  # 返回 1 并保存到变量
        """
        try:
            # 如果是字符串，先解析为JSON
            if isinstance(data, str):
                data = json.loads(data)

            # 解析JSONPath表达式
            if use_extended:
                jsonpath_expr = ext_parse(path)
            else:
                jsonpath_expr = parse(path)

            # 执行查询
            matches = jsonpath_expr.find(data)

            if not matches:
                log.debug(f"JSONPath '{path}' 未找到匹配项")
                result = default
            else:
                # 提取匹配的值
                values = [match.value for match in matches]

                # 如果只有一个结果，直接返回值；否则返回列表
                result = values[0] if len(values) == 1 else values

            # 如果指定了变量名，保存到变量
            if variable_name:
                self.variables[variable_name] = result
                log.info(f"提取并保存变量 '{variable_name}' = {result}")

            return result

        except JSONPathError as e:
            log.error(f"JSONPath解析错误: {e}")
            return default
        except json.JSONDecodeError as e:
            log.error(f"JSON解析错误: {e}")
            return default
        except Exception as e:
            log.error(f"提取失败: {e}")
            return default

    def extract_multiple(
        self,
        data: Union[Dict, str],
        extractions: Dict[str, Union[str, Dict]]
    ) -> Dict[str, Any]:
        """
        批量提取多个值

        Args:
            data: JSON数据
            extractions: 提取配置，格式为 {变量名: JSONPath} 或 {变量名: {path: JSONPath, default: 默认值}}

        Returns:
            提取结果字典

        Examples:
            >>> extractor = JSONPathExtractor()
            >>> data = {"code": 200, "data": {"token": "abc", "userId": 123}}
            >>> config = {
            ...     "token": "$.data.token",
            ...     "user_id": {"path": "$.data.userId", "default": 0}
            ... }
            >>> extractor.extract_multiple(data, config)
            {"token": "abc", "user_id": 123}
        """
        results = {}

        for var_name, config in extractions.items():
            if isinstance(config, str):
                # 简单格式：直接是JSONPath
                path = config
                default = None
            elif isinstance(config, dict):
                # 详细格式：包含path和default
                path = config.get("path", "")
                default = config.get("default")
            else:
                log.warning(f"无效的提取配置: {var_name}")
                continue

            value = self.extract(data, path, var_name, default)
            results[var_name] = value

        return results

    def get_variable(self, name: str, default: Any = None) -> Any:
        """
        获取已保存的变量

        Args:
            name: 变量名
            default: 默认值

        Returns:
            变量值
        """
        return self.variables.get(name, default)

    def set_variable(self, name: str, value: Any) -> None:
        """
        手动设置变量

        Args:
            name: 变量名
            value: 变量值
        """
        self.variables[name] = value
        log.debug(f"设置变量 '{name}' = {value}")

    def get_all_variables(self) -> Dict[str, Any]:
        """获取所有变量"""
        return self.variables.copy()

    def clear_variables(self) -> None:
        """清空所有变量"""
        self.variables.clear()
        log.debug("已清空所有变量")

    def replace_variables(self, text: str) -> str:
        """
        替换文本中的变量引用

        Args:
            text: 包含变量引用的文本，格式为 ${变量名}

        Returns:
            替换后的文本

        Examples:
            >>> extractor = JSONPathExtractor()
            >>> extractor.set_variable("token", "abc123")
            >>> extractor.replace_variables("Bearer ${token}")
            "Bearer abc123"
        """
        def replacer(match):
            var_name = match.group(1)
            value = self.get_variable(var_name)
            if value is None:
                log.warning(f"变量 '{var_name}' 不存在")
                return match.group(0)  # 保留原文
            return str(value)

        # 使用正则表达式替换 ${变量名} 格式的引用
        pattern = r'\$\{([^}]+)\}'
        return re.sub(pattern, replacer, text)

    def replace_in_dict(self, data: Dict) -> Dict:
        """
        递归替换字典中的变量引用

        Args:
            data: 包含变量引用的字典

        Returns:
            替换后的字典

        Examples:
            >>> extractor = JSONPathExtractor()
            >>> extractor.set_variable("user_id", 123)
            >>> data = {"userId": "${user_id}", "action": "login"}
            >>> extractor.replace_in_dict(data)
            {"userId": "123", "action": "login"}
        """
        if not isinstance(data, dict):
            return data

        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.replace_variables(value)
            elif isinstance(value, dict):
                result[key] = self.replace_in_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    self.replace_variables(item) if isinstance(item, str)
                    else self.replace_in_dict(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value

        return result

    def save_response(self, name: str, response: Dict) -> None:
        """
        保存响应数据供后续使用

        Args:
            name: 响应名称
            response: 响应数据
        """
        self.response_cache[name] = response
        log.debug(f"保存响应 '{name}'")

    def get_response(self, name: str) -> Optional[Dict]:
        """
        获取保存的响应数据

        Args:
            name: 响应名称

        Returns:
            响应数据
        """
        return self.response_cache.get(name)

    def extract_from_response(
        self,
        response_name: str,
        path: str,
        variable_name: Optional[str] = None,
        default: Any = None
    ) -> Any:
        """
        从保存的响应中提取数据

        Args:
            response_name: 响应名称
            path: JSONPath表达式
            variable_name: 变量名
            default: 默认值

        Returns:
            提取的值
        """
        response = self.get_response(response_name)
        if response is None:
            log.warning(f"响应 '{response_name}' 不存在")
            return default

        return self.extract(response, path, variable_name, default)


# 全局实例，方便直接使用
jsonpath_extractor = JSONPathExtractor()
