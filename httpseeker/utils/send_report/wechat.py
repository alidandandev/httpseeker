#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpseeker.common.log import log
from httpseeker.core.get_conf import httpseeker_config


class WeChat:
    def __init__(self, content: dict):
        self.content = content

    def send(self) -> None:
        # 发送企业微信消息
        try:
            import requests

            headers = {'Content-Type': 'application/json; charset=utf-8', 'Connection': 'close'}
            data = {
                'msgtype': 'markdown',
                'markdown': {
                    'content': f'# {httpseeker_config.TEST_REPORT_TITLE}\n'
                    f'> 👤 测试人员: **{httpseeker_config.TESTER_NAME}**\n'
                    f'> 🤖 测试结果: **{self.content["result"]}**\n'
                    f"> ✅ 通过用例: <font color='info'>**{self.content['passed']}**</font>\n"
                    f'> 🔧 失败用例: **{self.content["failed"]}**\n'
                    f'> ❌ 错误用例: **{self.content["error"]}**\n'
                    f'> ⚠️ 跳过用例: **{self.content["skipped"]}**\n'
                    f'> ⌛ 开始时间: **{self.content["started_time"]}**\n'
                    f'> ⏱️ 执行耗时: **{self.content["elapsed"]}**\n'
                    f'> ➡️ 查看报告: [点击跳转]({httpseeker_config.JENKINS_URL})'
                },
            }
            response = requests.session().post(
                url=httpseeker_config.WECHAT_WEBHOOK,
                json=data,
                headers=headers,
                proxies=httpseeker_config.WECHAT_PROXY,  # type: ignore
            )
            response.raise_for_status()
        except Exception as e:
            log.error(f'企业微信消息发送异常: {e}')
        else:
            log.success('企业微信发送成功')
