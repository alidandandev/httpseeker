#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
如何在 HttpSeeker 项目中集成 Telegram Notifier 的示例

这个文件展示了两种集成方式：
1. 完全替换原有的 Telegram 推送
2. 作为独立服务单独调用
"""

import sys
import os

# 方式 1：将 telegram_notifier 添加到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_notifier import send_notification, send_message


# ========== 集成示例 1：在 run.py 中使用 ==========
def integration_example_1(test_result):
    """
    替换 httpseeker/run.py 中的 Telegram 推送

    原代码（第 148-149 行）：
        if httpseeker_config.TELEGRAM_SEND:
            Telegram(test_result).send()

    新代码：
    """
    from httpseeker.core.get_conf import httpseeker_config

    if httpseeker_config.TELEGRAM_SEND:
        # 使用独立的 Telegram Notifier 模块
        config_path = os.path.join(
            os.path.dirname(__file__),
            'config.toml'
        )
        send_notification(test_result, config_path=config_path)


# ========== 集成示例 2：作为独立服务 ==========
def integration_example_2():
    """
    在测试结束后，通过命令行调用独立的 Telegram Notifier

    可以在 pytest hooks 中调用，或在测试脚本结束时调用
    """
    import subprocess

    # 从 YAML 报告文件读取测试结果（假设已有）
    yaml_report_path = '/path/to/yaml/report.yaml'

    # 转换为 JSON 格式
    # ... 转换逻辑 ...

    # 保存为 JSON 文件
    json_report_path = '/tmp/test_report.json'

    # 调用命令行工具发送
    subprocess.run([
        'python', '-m', 'telegram_notifier.cli',
        '--report-file', json_report_path,
        '--config', '/path/to/config.toml'
    ])


# ========== 集成示例 3：在 conftest.py 中使用 ==========
def integration_example_3():
    """
    在 pytest 的 conftest.py 中添加 hook，测试结束后自动发送

    在 httpseeker/conftest.py 中添加：
    """
    import pytest

    @pytest.hookimpl(tryfirst=True)
    def pytest_sessionfinish(session, exitstatus):
        """测试会话结束时的钩子"""
        # 获取测试结果统计
        from telegram_notifier import send_notification
        from httpseeker.utils.time_control import get_current_time

        # 构建报告数据
        stats = session.testscollected
        report_data = {
            'result': 'Success' if exitstatus == 0 else 'Failed',
            'passed': session.testscollected - session.testsfailed,
            'failed': session.testsfailed,
            'error': 0,
            'skipped': 0,
            'started_time': get_current_time(),
            'elapsed': f'{session.duration:.2f}s'
        }

        # 发送通知
        send_notification(
            report_data,
            config_path='/path/to/telegram_notifier/config.toml'
        )


# ========== 集成示例 4：发送自定义消息 ==========
def integration_example_4():
    """
    在代码的关键节点发送自定义通知消息
    """
    # 例如：测试开始时发送通知
    send_message(
        "*测试开始*\n"
        "项目: HttpSeeker\n"
        "环境: Production\n"
        "执行人: Rookie",
        config_path='/path/to/config.toml'
    )

    # 测试过程中的错误通知
    try:
        # ... 测试代码 ...
        pass
    except Exception as e:
        send_message(
            f"❌ *测试执行异常*\n\n"
            f"错误信息: `{str(e)}`\n"
            f"请及时查看！",
            config_path='/path/to/config.toml'
        )


# ========== 集成示例 5：批量发送多个报告 ==========
def integration_example_5():
    """
    对多个测试项目分别发送报告
    """
    from telegram_notifier import TelegramNotifier, load_config

    # 加载配置
    config = load_config('/path/to/config.toml')
    notifier = TelegramNotifier(config)

    # 项目列表
    projects = [
        {
            'name': 'Dz_like_bofa_h5',
            'passed': 10,
            'failed': 0
        },
        {
            'name': 'bofa_admin',
            'passed': 8,
            'failed': 2
        }
    ]

    # 为每个项目发送报告
    for project in projects:
        report_data = {
            'result': 'Success' if project['failed'] == 0 else 'Failed',
            'passed': project['passed'],
            'failed': project['failed'],
            'error': 0,
            'skipped': 0,
            'started_time': '2024-01-01 10:00:00',
            'elapsed': '5.2s'
        }

        # 修改配置中的项目名
        original_name = notifier.config.project_name
        notifier.config.project_name = project['name']

        # 发送报告
        notifier.send_test_report(report_data)

        # 恢复配置
        notifier.config.project_name = original_name


if __name__ == '__main__':
    print("这个文件包含集成示例，请根据需要复制代码到你的项目中")
    print("\n可用的集成方式：")
    print("1. integration_example_1 - 在 run.py 中替换原有推送")
    print("2. integration_example_2 - 作为独立服务调用")
    print("3. integration_example_3 - 在 pytest hooks 中使用")
    print("4. integration_example_4 - 发送自定义消息")
    print("5. integration_example_5 - 批量发送多个报告")
