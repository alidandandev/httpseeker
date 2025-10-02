#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class HttpSeekerErrorMixin:
    """HttpSeeker错误基类"""

    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class ConfigInitError(HttpSeekerErrorMixin, RuntimeError):
    """配置初始化错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class AuthError(HttpSeekerErrorMixin, ValueError):
    """认证错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class RequestDataParseError(HttpSeekerErrorMixin, ValueError):
    """请求数据解析错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class CorrelateTestCaseError(HttpSeekerErrorMixin, ValueError):
    """关联测试用例错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class SendRequestError(HttpSeekerErrorMixin, RuntimeError):
    """发送请求错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class JsonPathFindError(HttpSeekerErrorMixin, ValueError):
    """JsonPath查找错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class VariableError(HttpSeekerErrorMixin, ValueError):
    """变量错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class SQLSyntaxError(HttpSeekerErrorMixin, ValueError):
    """SQL语法错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class AssertSyntaxError(HttpSeekerErrorMixin, ValueError):
    """断言格式错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class AssertError(HttpSeekerErrorMixin, AssertionError):
    """断言错误"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)
