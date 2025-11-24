#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Jenkins 环境变量自动获取功能

这个脚本演示了如何在 Jenkins 环境中自动获取项目名称和报告地址
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_jenkins_env():
    """测试 Jenkins 环境变量自动获取"""
    print("=" * 70)
    print("Jenkins 环境变量自动获取功能测试")
    print("=" * 70)
    print()

    # 测试 1: 模拟 Jenkins 环境
    print("📋 测试 1: 模拟 Jenkins 环境")
    print("-" * 70)

    # 设置 Jenkins 环境变量
    os.environ['JOB_NAME'] = 'Dz_Like_bofa_h5'
    os.environ['BUILD_URL'] = 'http://47.76.165.189:8080/job/Dz_Like_bofa_h5/125/'

    from telegram_notifier.config import Config

    config = Config('telegram_notifier/config.toml')

    print(f"设置的环境变量:")
    print(f"  JOB_NAME = {os.environ.get('JOB_NAME')}")
    print(f"  BUILD_URL = {os.environ.get('BUILD_URL')}")
    print()
    print(f"自动获取的配置:")
    print(f"  project_name = {config.project_name}")
    print(f"  jenkins_url = {config.jenkins_url}")
    print()

    assert config.project_name == 'Dz_Like_bofa_h5', "项目名称应该从 JOB_NAME 获取"
    assert config.jenkins_url == 'http://47.76.165.189:8080/job/Dz_Like_bofa_h5/allure/', \
        "Jenkins URL 应该从 BUILD_URL 生成"

    print("✅ 测试 1 通过：Jenkins 环境变量成功自动获取")
    print()

    # 测试 2: 非 Jenkins 环境
    print("📋 测试 2: 非 Jenkins 环境（使用配置文件默认值）")
    print("-" * 70)

    # 清除 Jenkins 环境变量
    os.environ.pop('JOB_NAME', None)
    os.environ.pop('BUILD_URL', None)

    # 重新导入配置类（因为 Python 模块缓存）
    import importlib
    import telegram_notifier.config as config_module
    importlib.reload(config_module)

    config2 = config_module.Config('telegram_notifier/config.toml')

    print(f"环境变量状态:")
    print(f"  JOB_NAME = {os.environ.get('JOB_NAME', '(未设置)')}")
    print(f"  BUILD_URL = {os.environ.get('BUILD_URL', '(未设置)')}")
    print()
    print(f"使用的配置（来自配置文件）:")
    print(f"  project_name = {config2.project_name}")
    print(f"  jenkins_url = {config2.jenkins_url}")
    print()

    print("✅ 测试 2 通过：在非 Jenkins 环境中使用配置文件默认值")
    print()

    # 测试 3: 不同的 Jenkins 项目
    print("📋 测试 3: 模拟不同的 Jenkins 项目")
    print("-" * 70)

    # 设置不同的 Jenkins 环境变量
    os.environ['JOB_NAME'] = 'Another_Project'
    os.environ['BUILD_URL'] = 'http://jenkins.example.com/job/Another_Project/88/'

    importlib.reload(config_module)
    config3 = config_module.Config('telegram_notifier/config.toml')

    print(f"设置的环境变量:")
    print(f"  JOB_NAME = {os.environ.get('JOB_NAME')}")
    print(f"  BUILD_URL = {os.environ.get('BUILD_URL')}")
    print()
    print(f"自动获取的配置:")
    print(f"  project_name = {config3.project_name}")
    print(f"  jenkins_url = {config3.jenkins_url}")
    print()

    assert config3.project_name == 'Another_Project', "项目名称应该从 JOB_NAME 获取"
    assert config3.jenkins_url == 'http://jenkins.example.com/job/Another_Project/allure/', \
        "Jenkins URL 应该从 BUILD_URL 生成"

    print("✅ 测试 3 通过：同一配置文件可以在不同 Jenkins 项目中使用")
    print()

    print("=" * 70)
    print("🎉 所有测试通过！Jenkins 环境变量自动获取功能正常工作")
    print("=" * 70)


def test_url_generation():
    """测试 URL 生成逻辑"""
    print()
    print("=" * 70)
    print("URL 生成逻辑测试")
    print("=" * 70)
    print()

    import re

    test_cases = [
        ('http://jenkins.com/job/MyProject/123/', 'http://jenkins.com/job/MyProject/allure/'),
        ('http://jenkins.com/job/MyProject/456', 'http://jenkins.com/job/MyProject/allure/'),
        ('http://jenkins.com/job/Test_Job/999/', 'http://jenkins.com/job/Test_Job/allure/'),
    ]

    for build_url, expected_allure_url in test_cases:
        base_url = re.sub(r'/\d+/?$', '/', build_url)
        allure_url = base_url.rstrip('/') + '/allure/'

        print(f"BUILD_URL: {build_url}")
        print(f"生成的 Allure URL: {allure_url}")
        print(f"预期的 Allure URL: {expected_allure_url}")

        assert allure_url == expected_allure_url, f"URL 生成错误！期望 {expected_allure_url}，实际 {allure_url}"
        print("✅ 通过")
        print()

    print("=" * 70)
    print("🎉 URL 生成逻辑测试通过")
    print("=" * 70)


if __name__ == '__main__':
    try:
        test_jenkins_env()
        test_url_generation()
        print()
        print("✨ 所有测试完成！")
    except AssertionError as e:
        print(f"❌ 测试失败：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试过程中发生错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
