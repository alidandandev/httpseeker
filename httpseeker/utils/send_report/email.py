#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import smtplib
import time

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Template

from httpseeker.common.log import log
from httpseeker.core.get_conf import httpseeker_config
from httpseeker.core.path_conf import httpseeker_path
from httpseeker.enums.email_type import EmailType
from httpseeker.utils.file_control import get_file_property


class SendEmail:
    def __init__(self, content: dict, filename: str | None = None):
        self.content = content
        self.filename = filename

    def take_report(self) -> MIMEMultipart:
        """
        获取报告
        """
        msg = MIMEMultipart()
        msg['Subject'] = httpseeker_config.TEST_REPORT_TITLE
        msg['From'] = httpseeker_config.EMAIL_USER
        msg['date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
        self.content.update({'test_title': httpseeker_config.TEST_REPORT_TITLE})
        self.content.update({'tester_name': httpseeker_config.TESTER_NAME})

        # 邮件正文
        with open(os.path.join(httpseeker_path.html_email_report_dir, 'email_report.html'), 'r', encoding='utf-8') as f:
            html = Template(f.read())

        mail_body = MIMEText(html.render(**self.content), _subtype='html', _charset='utf-8')
        msg.attach(mail_body)

        # 读取要发送的附件
        if self.filename:
            with open(self.filename, 'rb') as f:
                annex_body = f.read()
                # 邮件附件
                att1 = MIMEApplication(annex_body)
                att1['Content-Type'] = 'application/octet-stream'
                att1['Content-Disposition'] = f'attachment; filename={get_file_property(self.filename)[0]}'
                msg.attach(att1)

        return msg

    def take_error(self) -> MIMEMultipart:
        """
        获取错误信息
        """
        msg = MIMEMultipart()
        msg['Subject'] = 'HttpSeeker 运行异常通知'
        msg['From'] = httpseeker_config.EMAIL_USER
        msg['date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')

        # 邮件正文
        with open(
            os.path.join(httpseeker_path.html_email_report_dir, 'email_notification.html'), 'r', encoding='utf-8'
        ) as f:
            html = Template(f.read())

        mail_body = MIMEText(html.render(**self.content), _subtype='html', _charset='utf-8')
        msg.attach(mail_body)

        return msg

    def _send(self, msg_type: int) -> None:
        """
        发送邮件
        """
        msg = ''
        if msg_type == EmailType.REPORT:
            msg = self.take_report().as_string()
        elif msg_type == EmailType.ERROR:
            msg = self.take_error().as_string()
        if httpseeker_config.EMAIL_SSL:
            smtp = smtplib.SMTP_SSL(host=httpseeker_config.EMAIL_SERVER, port=httpseeker_config.EMAIL_PORT)
        else:
            smtp = smtplib.SMTP(host=httpseeker_config.EMAIL_SERVER, port=httpseeker_config.EMAIL_PORT)
        smtp.login(httpseeker_config.EMAIL_USER, httpseeker_config.EMAIL_PASSWORD)
        smtp.sendmail(httpseeker_config.EMAIL_USER, httpseeker_config.EMAIL_SEND_TO, msg)
        smtp.quit()

    def send_report(self) -> None:
        try:
            self._send(0)
        except Exception as e:
            log.error(f'测试报告邮件发送失败: {e}')
        else:
            log.info('测试报告邮件发送成功')

    def send_error(self) -> None:
        try:
            self._send(1)
        except Exception as e:
            log.error(f'运行异常通知邮件发送失败: {e}')
        else:
            log.info('运行异常通知邮件发送成功')
