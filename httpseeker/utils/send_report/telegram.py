#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpseeker.common.log import log
from httpseeker.core.get_conf import httpseeker_config


class Telegram:
    def __init__(self, content: dict):
        self.content = content

    def send(self) -> None:
        # 发送Telegram消息
        try:
            import requests

            # 清理chat_id，去除可能的空格
            chat_id = str(httpseeker_config.TELEGRAM_CHAT_ID).strip()

            # 根据测试结果显示不同的状态标识
            result_emoji = '✅ PASS ✅' if self.content['result'] == 'Success' else '❌ FAIL ❌'

            # 构建消息文本（使用Markdown格式）
            message_text = (
                f'{result_emoji}\n'
                f'*{httpseeker_config.PROJECT_NAME}接口自动化测试报告*\n'
                f'👤 测试人员: {httpseeker_config.TESTER_NAME}\n'
                f'✅ 通过用例: {self.content["passed"]}\n'
                f'🔧 失败用例: {self.content["failed"]}\n'
                f'❌ 错误用例: {self.content["error"]}\n'
                f'⚠️ 跳过用例: {self.content["skipped"]}\n'
                f'⌛ 开始时间: {self.content["started_time"]}\n'
                f'⏱️ 执行耗时: {self.content["elapsed"]}\n'
                f'➡️ [查看详情]({httpseeker_config.JENKINS_URL})'
            )

            # Telegram Bot API URL
            url = f'https://api.telegram.org/bot{httpseeker_config.TELEGRAM_BOT_TOKEN}/sendMessage'

            # 请求参数
            data = {
                'chat_id': chat_id,
                'text': message_text,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': False,
            }

            # 发送请求
            response = requests.session().post(
                url=url,
                json=data,
                proxies=httpseeker_config.TELEGRAM_PROXY,  # type: ignore
            )

            # 先获取响应内容，用于详细错误信息
            result = response.json()

            # 检查HTTP状态码
            response.raise_for_status()

            # 检查返回结果
            if not result.get('ok'):
                raise Exception(f"Telegram API返回错误: {result.get('description', 'Unknown error')}")

        except requests.exceptions.HTTPError as e:
            # HTTP错误，尝试解析响应中的错误信息
            try:
                error_detail = response.json()
                log.error(f'Telegram消息发送异常: {e} - {error_detail.get("description", "未知错误")}')
            except:
                log.error(f'Telegram消息发送异常: {e}')
        except Exception as e:
            log.error(f'Telegram消息发送异常: {e}')
        else:
            log.success('Telegram消息发送成功')
