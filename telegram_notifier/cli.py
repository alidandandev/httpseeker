#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""命令行接口"""
import argparse
import json
import sys
from pathlib import Path

from . import send_notification, send_message, __version__


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Telegram Notifier - 独立的 Telegram 消息推送工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 发送测试报告
  python -m telegram_notifier.cli --report '{"result": "Success", "passed": 10, "failed": 0}'

  # 发送自定义消息
  python -m telegram_notifier.cli --message "测试完成"

  # 使用自定义配置文件
  python -m telegram_notifier.cli --config /path/to/config.toml --message "Hello"

  # 从 JSON 文件读取报告数据
  python -m telegram_notifier.cli --report-file report.json
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'Telegram Notifier v{__version__}'
    )

    parser.add_argument(
        '-c', '--config',
        type=str,
        help='配置文件路径 (默认: telegram_notifier/config.toml)'
    )

    # 创建互斥组：报告或消息
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '-r', '--report',
        type=str,
        help='测试报告数据 (JSON 格式字符串)'
    )

    group.add_argument(
        '-f', '--report-file',
        type=str,
        help='测试报告数据文件 (JSON 文件路径)'
    )

    group.add_argument(
        '-m', '--message',
        type=str,
        help='自定义消息内容'
    )

    parser.add_argument(
        '--parse-mode',
        type=str,
        choices=['Markdown', 'HTML'],
        default='Markdown',
        help='消息格式 (默认: Markdown)'
    )

    args = parser.parse_args()

    try:
        # 发送测试报告
        if args.report:
            report_data = json.loads(args.report)
            success = send_notification(report_data, args.config)

        # 从文件读取测试报告
        elif args.report_file:
            report_file = Path(args.report_file)
            if not report_file.exists():
                print(f"错误: 文件不存在: {args.report_file}", file=sys.stderr)
                sys.exit(1)

            with open(report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)

            success = send_notification(report_data, args.config)

        # 发送自定义消息
        elif args.message:
            success = send_message(args.message, args.config, args.parse_mode)

        else:
            parser.print_help()
            sys.exit(1)

        # 根据发送结果退出
        sys.exit(0 if success else 1)

    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
