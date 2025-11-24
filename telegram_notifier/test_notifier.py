#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Telegram Notifier 测试脚本"""

from telegram_notifier import send_notification, send_message


def test_send_report():
    """测试发送测试报告"""
    print("测试发送测试报告...")

    report_data = {
        'result': 'Success',
        'passed': 10,
        'failed': 0,
        'error': 0,
        'skipped': 0,
        'started_time': '2024-01-01 10:00:00',
        'elapsed': '5.2s'
    }

    success = send_notification(report_data)

    if success:
        print("✅ 测试报告发送成功！")
    else:
        print("❌ 测试报告发送失败！")

    return success


def test_send_message():
    """测试发送自定义消息"""
    print("\n测试发送自定义消息...")

    message = """
*Telegram Notifier 测试*

这是一条测试消息。

✅ 支持 Markdown 格式
📱 支持 Emoji
🔗 [支持链接](https://telegram.org)
    """.strip()

    success = send_message(message)

    if success:
        print("✅ 自定义消息发送成功！")
    else:
        print("❌ 自定义消息发送失败！")

    return success


def main():
    """主函数"""
    print("=" * 50)
    print("Telegram Notifier 测试")
    print("=" * 50)

    # 测试 1: 发送测试报告
    test1 = test_send_report()

    # 测试 2: 发送自定义消息
    test2 = test_send_message()

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    print(f"测试报告发送: {'✅ 成功' if test1 else '❌ 失败'}")
    print(f"自定义消息发送: {'✅ 成功' if test2 else '❌ 失败'}")
    print("=" * 50)


if __name__ == '__main__':
    main()
