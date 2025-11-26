#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配置管理模块"""
import os
from pathlib import Path
from typing import Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib


class Config:
    """配置类"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径，如果为 None 则使用默认路径
        """
        if config_path is None:
            # 默认使用当前目录下的 config.toml
            config_path = Path(__file__).parent / "config.toml"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        # 读取 TOML 配置文件
        with open(config_path, 'rb') as f:
            self.settings = tomllib.load(f)

        # 检查是否在 Jenkins 环境中运行
        jenkins_job_name = os.environ.get('JOB_NAME')
        jenkins_build_url = os.environ.get('BUILD_URL')

        # 如果在 Jenkins 环境中，自动覆盖项目名称
        if jenkins_job_name:
            self.settings['report']['project_name'] = jenkins_job_name

        # 如果在 Jenkins 环境中，自动生成 allure 报告地址
        if jenkins_build_url:
            # Jenkins环境变量存在，生成固定的allure报告地址（不包含构建编号）
            # 示例: http://host/job/jobname/123/ -> http://host/job/jobname/allure/
            import re
            # 移除最后的构建编号部分（通常是数字/）
            base_url = re.sub(r'/\d+/?$', '/', jenkins_build_url)
            self.settings['report']['jenkins_url'] = base_url.rstrip('/') + '/allure/'

        # Telegram 配置
        self.bot_token = self._get_value('telegram.bot_token', required=True)
        self.chat_id = str(self._get_value('telegram.chat_id', required=True)).strip()
        self.telegram_send = self._get_value('telegram.send', default=True)

        # 代理配置
        http_proxy = self._get_value('telegram.proxies.http', default='')
        https_proxy = self._get_value('telegram.proxies.https', default='')
        self.proxies = {
            'http': http_proxy if http_proxy else None,
            'https': https_proxy if https_proxy else None,
        }

        # 报告配置
        self.project_name = self._get_value('report.project_name', default='自动化测试')
        self.tester_name = self._get_value('report.tester_name', default='Tester')
        self.jenkins_url = self._get_value('report.jenkins_url', default='')

    def _get_value(self, path: str, required: bool = False, default=None):
        """
        从配置中获取值

        Args:
            path: 配置路径，使用点号分隔，如 'telegram.bot_token'
            required: 是否必需
            default: 默认值

        Returns:
            配置值
        """
        keys = path.split('.')
        value = self.settings

        try:
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            if required:
                raise ValueError(f"配置项 {path} 是必需的，但未找到")
            return default


def load_config(config_path: Optional[str] = None) -> Config:
    """
    加载配置

    Args:
        config_path: 配置文件路径

    Returns:
        Config 实例
    """
    return Config(config_path)
