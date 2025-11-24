#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Telegram 通知推送模块"""
import logging
from typing import Dict, Optional, Any

import requests

from .config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram 通知推送器"""

    def __init__(self, config: Config):
        """
        初始化 Telegram 通知推送器

        Args:
            config: 配置对象
        """
        self.config = config
        self.bot_token = config.bot_token
        self.chat_id = config.chat_id
        self.proxies = config.proxies
        self.api_url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'

    def send_test_report(self, report_data: Dict[str, Any]) -> bool:
        """
        发送测试报告

        Args:
            report_data: 测试报告数据，包含以下字段：
                - result: 测试结果 ('Success' 或 'Failed')
                - passed: 通过用例数
                - failed: 失败用例数
                - error: 错误用例数
                - skipped: 跳过用例数
                - started_time: 开始时间
                - elapsed: 执行耗时

        Returns:
            是否发送成功
        """
        if not self.config.telegram_send:
            logger.info("Telegram 推送功能已关闭")
            return False

        response = None
        try:
            # 根据测试结果显示不同的状态标识
            result_emoji = '✅ PASS ✅' if report_data.get('result') == 'Success' else '❌ FAIL ❌'

            # 构建消息文本（使用Markdown格式，与原始模板完全一致）
            message_text = (
                f'{result_emoji}\n'
                f'*{self.config.project_name}接口自动化测试报告*\n'
                f'👤 测试人员: {self.config.tester_name}\n'
                f'✅ 通过用例: {report_data.get("passed", 0)}\n'
                f'🔧 失败用例: {report_data.get("failed", 0)}\n'
                f'❌ 错误用例: {report_data.get("error", 0)}\n'
                f'⚠️ 跳过用例: {report_data.get("skipped", 0)}\n'
                f'⌛ 开始时间: {report_data.get("started_time", "N/A")}\n'
                f'⏱️ 执行耗时: {report_data.get("elapsed", "N/A")}\n'
                f'➡️ [查看详情]({self.config.jenkins_url})'
            )

            # 请求参数
            data = {
                'chat_id': self.chat_id,
                'text': message_text,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': False,
            }

            # 发送请求
            response = requests.post(
                url=self.api_url,
                json=data,
                proxies=self.proxies,
                timeout=30
            )

            # 先获取响应内容，用于详细错误信息
            result = response.json()

            # 检查HTTP状态码
            response.raise_for_status()

            # 检查返回结果
            if not result.get('ok'):
                raise Exception(f"Telegram API返回错误: {result.get('description', 'Unknown error')}")

            logger.info('Telegram 消息发送成功')
            return True

        except requests.exceptions.HTTPError as e:
            # HTTP错误，尝试解析响应中的错误信息
            if response is not None:
                try:
                    error_detail = response.json()
                    logger.error(f'Telegram 消息发送异常: {e} - {error_detail.get("description", "未知错误")}')
                except Exception:
                    logger.error(f'Telegram 消息发送异常: {e}')
            else:
                logger.error(f'Telegram 消息发送异常: {e}')
            return False

        except Exception as e:
            logger.error(f'Telegram 消息发送异常: {e}')
            return False

    def send_custom_message(self, message: str, parse_mode: str = 'Markdown') -> bool:
        """
        发送自定义消息

        Args:
            message: 消息内容
            parse_mode: 消息格式 ('Markdown' 或 'HTML')

        Returns:
            是否发送成功
        """
        if not self.config.telegram_send:
            logger.info("Telegram 推送功能已关闭")
            return False

        response = None
        try:
            # 请求参数
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': False,
            }

            # 发送请求
            response = requests.post(
                url=self.api_url,
                json=data,
                proxies=self.proxies,
                timeout=30
            )

            # 先获取响应内容，用于详细错误信息
            result = response.json()

            # 检查HTTP状态码
            response.raise_for_status()

            # 检查返回结果
            if not result.get('ok'):
                raise Exception(f"Telegram API返回错误: {result.get('description', 'Unknown error')}")

            logger.info('Telegram 消息发送成功')
            return True

        except requests.exceptions.HTTPError as e:
            # HTTP错误，尝试解析响应中的错误信息
            if response is not None:
                try:
                    error_detail = response.json()
                    logger.error(f'Telegram 消息发送异常: {e} - {error_detail.get("description", "未知错误")}')
                except Exception:
                    logger.error(f'Telegram 消息发送异常: {e}')
            else:
                logger.error(f'Telegram 消息发送异常: {e}')
            return False

        except Exception as e:
            logger.error(f'Telegram 消息发送异常: {e}')
            return False


def send_notification(report_data: Dict[str, Any], config_path: Optional[str] = None) -> bool:
    """
    便捷函数：发送测试报告通知

    Args:
        report_data: 测试报告数据
        config_path: 配置文件路径

    Returns:
        是否发送成功
    """
    from .config import load_config

    config = load_config(config_path)
    notifier = TelegramNotifier(config)
    return notifier.send_test_report(report_data)


def send_message(message: str, config_path: Optional[str] = None, parse_mode: str = 'Markdown') -> bool:
    """
    便捷函数：发送自定义消息

    Args:
        message: 消息内容
        config_path: 配置文件路径
        parse_mode: 消息格式

    Returns:
        是否发送成功
    """
    from .config import load_config

    config = load_config(config_path)
    notifier = TelegramNotifier(config)
    return notifier.send_custom_message(message, parse_mode)
