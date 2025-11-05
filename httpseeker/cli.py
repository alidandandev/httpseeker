#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys

from dataclasses import dataclass

import cappa

from cappa import Subcommands
from rich.traceback import install as rich_install
from typing_extensions import TYPE_CHECKING, Annotated

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from httpseeker.run import run
from httpseeker.utils.cli.about_testcase import generate_testcases, testcase_data_verify
from httpseeker.utils.cli.import_case_data import (
    import_apifox_case_data,
    import_git_case_data,
    import_har_case_data,
    import_jmeter_case_data,
    import_openapi_case_data,
    import_postman_case_data,
)
from httpseeker.utils.cli.version import get_version
from httpseeker.utils.rich_console import console

if TYPE_CHECKING:
    from cappa.parser import Value


def cmd_run_test_parse(value: Value) -> bool | Value:
    """运行测试命令参数解析"""
    if len(value) == 0:  # type: ignore
        return True
    else:
        return value


@cappa.command(name='httpseeker-cli')
@dataclass
class HttpSeekerCLI:
    version: Annotated[
        bool,
        cappa.Arg(
            short='-V',
            long=True,
            default=False,
            help='打印版本信息',
        ),
    ]
    run_test: Annotated[
        list[str] | None,
        cappa.Arg(
            value_name='<PYTEST 参数 / 无>',
            short='-r',
            long='--run',
            default=None,
            help='运行测试用例，不支持与其他命令同时使用，但支持自定义 pytest 运行参数，'
            '默认参数请查看 `httpseeker/run.py`',
            parse=cmd_run_test_parse,
            num_args=-1,
        ),
    ]
    env: Annotated[
        str | None,
        cappa.Arg(
            value_name='<环境文件>',
            long='--env',
            default=None,
            help='指定环境变量文件名 (例如: test.env, dev.env, pro.env)',
            required=False,
        ),
    ] = None
    conf: Annotated[
        str | None,
        cappa.Arg(
            value_name='<配置文件>',
            long='--conf',
            default=None,
            help='指定配置文件路径，支持相对路径和绝对路径 (例如: httpseeker/core/conf.toml)',
            required=False,
        ),
    ] = None
    auth: Annotated[
        str | None,
        cappa.Arg(
            value_name='<认证文件>',
            long='--auth',
            default=None,
            help='指定认证配置文件路径，支持相对路径和绝对路径 (例如: httpseeker/core/auth.yaml)',
            required=False,
        ),
    ] = None
    subcmd: Subcommands[TestCaseCLI | ImportCLI | None] = None

    def __call__(self) -> None:
        if self.version:
            get_version()
        if self.run_test:
            if self.version or self.subcmd:
                console.print('\n❌ 暂不支持 -r/--run 命令与其他 CLI 命令同时使用')
                raise cappa.Exit(code=1)
            # 构建额外参数字典
            extra_kwargs = {}
            if self.env is not None:
                extra_kwargs['global_env'] = self.env
            if self.conf is not None:
                # 支持相对路径：相对于当前工作目录
                conf_path = self.conf
                if not os.path.isabs(conf_path):
                    conf_path = os.path.abspath(conf_path)
                extra_kwargs['conf_path'] = conf_path
            if self.auth is not None:
                # 支持相对路径：相对于当前工作目录
                auth_path = self.auth
                if not os.path.isabs(auth_path):
                    auth_path = os.path.abspath(auth_path)
                extra_kwargs['auth_path'] = auth_path

            if isinstance(self.run_test, list):
                run(*self.run_test, **extra_kwargs)
            else:
                run(**extra_kwargs)


@cappa.command(name='testcase', help='测试用例工具')
@dataclass
class TestCaseCLI:
    data_verify: Annotated[
        str,
        cappa.Arg(
            value_name='<文件名 / ALL>',
            short='-c',
            long=True,
            default='',
            help='验证测试数据结构；当指定文件（文件名/绝对路径）时, 仅验证指定文件, 当指定 "all" 时, 验证所有文件',
            required=False,
        ),
    ]
    generate: Annotated[
        bool,
        cappa.Arg(
            short='-g',
            long=True,
            default=False,
            help='自动生成测试用例',
            required=False,
        ),
    ]

    def __call__(self) -> None:
        if self.data_verify:
            testcase_data_verify(self.data_verify)
        if self.generate:
            generate_testcases()


@cappa.command(name='import', help='导入测试数据')
@dataclass
class ImportCLI:
    openai: Annotated[
        tuple[str, str],
        cappa.Arg(
            value_name='<JSON文件 / URL> <项目名>',
            short='-o',
            long='--import-openapi',
            default=(),
            help='导入 OpenAPI 数据到 YAML 数据文件；支持 JSON 文件或 URL 导入，需要指定项目名',
            required=False,
        ),
    ]
    apifox: Annotated[
        tuple[str, str],
        cappa.Arg(
            value_name='<JSON文件> <项目名>',
            short='-a',
            long='--import-apifox',
            default=(),
            help='Beta：导入 Apifox 数据到 YAML 数据文件；支持 JSON 文件导入，需要指定项目名',
            required=False,
        ),
    ]
    har: Annotated[
        tuple[str, str],
        cappa.Arg(
            short='-h',
            long='--import-har',
            default=(),
            help='待开发：导入 HAR 文件',
            required=False,
        ),
    ]
    jmeter: Annotated[
        tuple[str, str],
        cappa.Arg(
            short='-j',
            long='--import-jmeter',
            default=(),
            help='待开发：导入 JMeter 测试数据',
            required=False,
        ),
    ]
    postman: Annotated[
        tuple[str, str],
        cappa.Arg(
            short='-p',
            long='--import-postman',
            default=(),
            help='待开发：导入 Postman 测试数据',
            required=False,
        ),
    ]
    git: Annotated[
        str,
        cappa.Arg(
            value_name='<GIT 地址>',
            long='--import-git',
            default='',
            help='导入 Git 仓库测试数据到本地',
            required=False,
        ),
    ]

    def __call__(self) -> None:
        if self.openai:
            import_openapi_case_data(self.openai)
        if self.apifox:
            import_apifox_case_data(self.apifox)
        if self.har:
            import_har_case_data(self.har)
        if self.jmeter:
            import_jmeter_case_data(self.jmeter)
        if self.postman:
            import_postman_case_data(self.postman)
        if self.git:
            import_git_case_data(self.git)


def cappa_invoke() -> None:
    """cli 执行程序"""
    rich_install()
    cappa.invoke(HttpSeekerCLI)


if __name__ == '__main__':
    cappa_invoke()
