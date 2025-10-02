#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpseeker.common.log import log
from httpseeker.core.get_conf import httpseeker_config


class FeiShu:
    def __init__(self, content: dict):
        self.content = content

    def send(self) -> None:
        # 发送飞书消息
        try:
            import requests

            headers = {'Content-Type': 'application/json; charset=utf-8', 'Connection': 'close'}
            data = {
                'msg_type': 'post',
                'content': {
                    'post': {
                        'zh_cn': {
                            'title': httpseeker_config.TEST_REPORT_TITLE,
                            'content': [
                                [{'tag': 'text', 'text': f'👤 测试人员: {httpseeker_config.TESTER_NAME}'}],
                                [{'tag': 'text', 'text': f'🤖 测试结果: {self.content["result"]}'}],
                                [{'tag': 'text', 'text': f'✅ 通过用例: {self.content["passed"]}'}],
                                [{'tag': 'text', 'text': f'🔧 失败用例: {self.content["failed"]}'}],
                                [{'tag': 'text', 'text': f'❌ 错误用例: {self.content["error"]}'}],
                                [{'tag': 'text', 'text': f'⚠️ 跳过用例: {self.content["skipped"]}'}],
                                [{'tag': 'text', 'text': f'⌛ 开始时间: {self.content["started_time"]}'}],
                                [{'tag': 'text', 'text': f'⏱️ 执行耗时: {self.content["elapsed"]}'}],
                                [{'tag': 'a', 'text': '➡️ 查看详情', 'href': f'{httpseeker_config.JENKINS_URL}'}],
                            ],
                        }
                    }
                },
            }
            response = requests.session().post(
                url=httpseeker_config.FEISHU_WEBHOOK,
                json=data,
                headers=headers,
                proxies=httpseeker_config.FEISHU_PROXY,  # type: ignore
            )
            response.raise_for_status()
        except Exception as e:
            log.error(f'飞书消息发送异常: {e}')
        else:
            log.success('飞书消息发送成功')
