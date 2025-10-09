#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Jenkins CI/CD 专用运行脚本"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from httpseeker.run import run

if __name__ == '__main__':
    # Jenkins 环境优化配置
    run(
        # 禁用自动生成测试用例（如果测试用例已存在）
        testcase_generate=False,
        # 禁用邮件发送（避免 EMAIL_SEND 相关错误）
        html_report=True,
        # 启用 allure 报告
        allure=True,
        allure_clear=True,
        # 更详细的日志输出
        log_level='-v',
        # 禁用警告信息
        disable_warnings=True,
    )
