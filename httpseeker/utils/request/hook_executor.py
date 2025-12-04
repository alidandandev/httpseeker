#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re

from typing import Any

from httpseeker.common.log import log
from httpseeker.enums.setup_type import SetupType
from httpseeker.enums.teardown_type import TeardownType


class HookExecutor:
    def __init__(self) -> None:
        # hook 开头: a-zA-Z_
        # hook 表达: ${func()} 或 ${func(1, 2)}
        self.func_re = re.compile(r'\${([a-zA-Z_]\w*\([$\w.\-/\s=,]*\))}')

    def _quote_string_args(self, func_call: str) -> str:
        """
        将函数调用中的未加引号的字符串参数自动加上引号
        例如: get_google_auth_code(action) -> get_google_auth_code("action")

        :param func_call: 函数调用字符串，如 get_google_auth_code(action)
        :return: 处理后的函数调用字符串
        """
        # 匹配函数名和参数部分
        match = re.match(r'(\w+)\((.*)\)', func_call)
        if not match:
            return func_call

        func_name = match.group(1)
        args_str = match.group(2).strip()

        if not args_str:
            return func_call

        # 分割参数
        args = [arg.strip() for arg in args_str.split(',')]
        quoted_args = []

        for arg in args:
            # 跳过空参数
            if not arg:
                quoted_args.append(arg)
                continue

            # 已经是字符串（带引号）
            if (arg.startswith('"') and arg.endswith('"')) or \
               (arg.startswith("'") and arg.endswith("'")):
                quoted_args.append(arg)
            # 是数字
            elif re.match(r'^-?\d+\.?\d*$', arg):
                quoted_args.append(arg)
            # 是布尔值
            elif arg in ('True', 'False', 'None'):
                quoted_args.append(arg)
            # 是变量引用（以$开头）
            elif arg.startswith('$'):
                quoted_args.append(arg)
            # 其他情况视为字符串，加上引号
            else:
                quoted_args.append(f'"{arg}"')

        return f'{func_name}({", ".join(quoted_args)})'

    def hook_func_value_replace(self, target: dict) -> Any:
        """
        执行除前后置 hook 以外的所有 hook 函数并替换为它的返回值

        :param target:
        :return:
        """
        # 数据排除
        setup = target['test_steps'].get('setup')
        teardown = target['test_steps'].get('teardown')
        setup_hooks_with_index = []
        teardown_hooks_with_index = []
        if setup:
            setup_hooks_with_index.extend(
                [(i, item) for i, item in enumerate(setup) if item.get(SetupType.HOOK) is not None]
            )
            if setup_hooks_with_index:
                target['test_steps']['setup'] = [
                    item for item in target['test_steps']['setup'] if item.get(SetupType.HOOK) is None
                ]
        if teardown:
            teardown_hooks_with_index.extend(
                [(i, item) for i, item in enumerate(teardown) if item.get(TeardownType.HOOK) is not None]
            )
            if teardown_hooks_with_index:
                target['test_steps']['teardown'] = [
                    item for item in target['test_steps']['teardown'] if item.get(TeardownType.HOOK) is None
                ]

        str_target = json.dumps(target, ensure_ascii=False)

        match = self.func_re.search(str_target)
        if not match:
            return target

        # hook 返回值替换
        # 创建命名空间字典，用于存储导入的函数
        hook_namespace = {}
        exec('from httpseeker.core.hooks import *', hook_namespace)
        for match in self.func_re.finditer(str_target):
            hook_key = match.group(1)
            # 自动为未加引号的字符串参数添加引号
            quoted_hook_key = self._quote_string_args(hook_key)
            try:
                # 使用相同的命名空间执行函数调用
                exec(f'result = {quoted_hook_key}', hook_namespace)
                value = str(hook_namespace['result'])
                str_target = self.func_re.sub(value, str_target, 1)
                log.info(f'请求数据函数 {hook_key} 返回值替换完成')
            except Exception as e:
                log.error(f'请求数据函数 {hook_key} 返回值替换失败: {e}')
                raise e

        dict_target = json.loads(str_target)

        # 数据还原
        if setup:
            if setup_hooks_with_index:
                for i, item in setup_hooks_with_index:
                    target['test_steps']['setup'].insert(i, item)
        if teardown:
            if teardown_hooks_with_index:
                for i, item in teardown_hooks_with_index:
                    target['test_steps']['teardown'].insert(i, item)

        return dict_target

    def exec_hook_func(self, hook_var: str) -> None:
        """
        执行 hook 函数不返回任何值

        :param hook_var:
        :return:
        """
        key = self.func_re.search(hook_var)
        func = key.group(1)
        # 自动为未加引号的字符串参数添加引号
        quoted_func = self._quote_string_args(func)
        hook_namespace = {}
        exec('from httpseeker.core.hooks import *', hook_namespace)
        log.info(f'执行 hook：{func}')
        exec(quoted_func, hook_namespace)

    @staticmethod
    def exec_any_code(code: str) -> bool:
        """
        执行任何函数

        :param code:
        :return:
        """
        exec('import os')
        exec('import sys')
        result = eval(code)
        log.info(f'执行代码：{code}')
        return result


hook_executor = HookExecutor()
