#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpseeker.common.log import log
from httpseeker.core.get_conf import httpseeker_config


class DingDing:
    def __init__(self, content: dict):
        self.content = content

    def send(self) -> None:
        try:
            import requests

            headers = {'Content-Type': 'application/json; charset=utf-8', 'Connection': 'close'}
            data = {
                'msgtype': 'markdown',
                'markdown': {
                    'title': httpseeker_config.TEST_REPORT_TITLE,
                    'text': f'> ## {httpseeker_config.PROJECT_NAME} 自动化测试报告\n\n'
                    f'> 👤 测试人员: {httpseeker_config.TESTER_NAME}\n\n'
                    f'> 🤖 测试结果: {self.content["result"]}\n\n'
                    f'> ✅ 通过用例: {self.content["passed"]}\n\n'
                    f'> 🔧 失败用例: {self.content["failed"]}\n\n'
                    f'> ❌ 错误用例: {self.content["error"]}\n\n'
                    f'> ⚠️ 跳过用例: {self.content["skipped"]}\n\n'
                    f'> ⌛ 开始时间: {self.content["started_time"]}\n\n'
                    f'> ⏱️ 执行耗时: {self.content["elapsed"]}\n\n'
                    f'> ➡️ [查看详情]({httpseeker_config.JENKINS_URL})',
                },
            }
            response = requests.session().post(
                url=httpseeker_config.DINGDING_WEBHOOK,
                json=data,
                headers=headers,
                proxies=httpseeker_config.DINGDING_PROXY,  # type: ignore
            )
            response.raise_for_status()
        except Exception as e:
            log.error(f'钉钉消息发送异常: {e}')
        else:
            log.success('钉钉消息发送成功')
