#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Notifier - 独立的 Telegram 消息推送模块

提供测试报告推送和自定义消息推送功能
"""

from .config import Config, load_config
from .notifier import TelegramNotifier, send_notification, send_message

__version__ = '1.0.0'
__all__ = [
    'Config',
    'load_config',
    'TelegramNotifier',
    'send_notification',
    'send_message',
]
