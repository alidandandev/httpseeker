#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动注册用户并充值脚本
功能：
1. 生成随机手机号并注册新用户
2. 使用管理员账号登录
3. 查询新注册用户的ID
4. 为新用户充值20000
5. 更新auth.yaml文件中的账号信息
"""

import os
import sys
import requests
import yaml
from pathlib import Path
from faker import Faker
from jsonpath_ng import parse

# 添加项目根目录到系统路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from core.hooks import random_phone, get_google_auth_code

# 初始化Faker
faker = Faker(locale='zh_CN')


class AutoRegisterAndRecharge:
    """自动注册并充值用户"""

    def __init__(self):
        self.phone = None
        self.user_id = None
        self.admin_token = None
        self.session = requests.Session()

    def step1_generate_phone(self):
        """步骤1: 生成随机手机号"""
        self.phone = random_phone()
        print(f"✓ 步骤1: 生成随机手机号: {self.phone}")
        return self.phone

    def step2_register_user(self):
        """步骤2: 注册新用户"""
        url = "https://bofa.amigosqat.com/cdb/api/auth/reg_v2"

        # 生成随机名字
        real_name = faker.name()

        payload = {
            "account": self.phone,
            "countryCode": "86",
            "invitationCode": "d1yrkg",
            "password": "O4zAs9Mz4aoYOirIST4Xyg==",
            "validateCode": "",
            "uuid": "",
            "phoneValidateCode": "",
            "realName": real_name
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            print(f"✓ 步骤2: 注册用户成功")
            print(f"  - 手机号: {self.phone}")
            print(f"  - 姓名: {real_name}")
            print(f"  - 响应: {result}")
            return result
        except Exception as e:
            print(f"✗ 步骤2: 注册用户失败: {e}")
            raise

    def step3_generate_google_code(self,secret_key = "UOZ74J5U3UMZR2OD"):
        """步骤3: 生成谷歌验证码"""
        google_code = get_google_auth_code(secret_key)
        print(f"✓ 步骤3: 生成谷歌验证码: {google_code}")
        return google_code

    def step4_admin_login(self, google_code):
        """步骤4: 管理员登录获取token"""
        url = "https://sea2admin.amigosqat.com/cdb/account/login"

        payload = {
            "username": "rookies",
            "password": "O4zAs9Mz4aoYOirIST4Xyg==",
            "ggcode": google_code
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

            # 提取token
            if result.get("code") == 20000 and result.get("success"):
                self.admin_token = result["data"]["token"]
                print(f"✓ 步骤4: 管理员登录成功")
                print(f"  - Token: {self.admin_token[:50]}...")
                return self.admin_token
            else:
                raise Exception(f"登录失败: {result}")
        except Exception as e:
            print(f"✗ 步骤4: 管理员登录失败: {e}")
            raise

    def step5_get_user_id(self):
        """步骤5: 查询用户信息获取ID"""
        url = f"https://sea2admin.amigosqat.com/cdb/dzuser/user/getPartList"

        params = {
            "page": 1,
            "limit": 10,
            "str": self.phone,
            "dzstatus": "",
            "vipType": "",
            "expVipType": "",
            "userType": 1,
            "registerIp": "",
            "lastIp": "",
            "levels": 0,
            "expireTimes": "",
            "expireTimee": "",
            "expStartTime": "",
            "expEndTime": "",
            "sourceInvitationCode": "",
            "walletAddress": "",
            "gmt": "",
            "countryCodeNumber": "",
            "realName": "",
            "lastIpCity": "",
            "email": ""
        }

        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "authorization": self.admin_token
        }

        try:
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            result = response.json()

            # 使用jsonpath提取用户ID
            jsonpath_expr = parse("$.data.records[*].id")
            matches = jsonpath_expr.find(result)

            if matches:
                self.user_id = matches[0].value
                print(f"✓ 步骤5: 查询用户信息成功")
                print(f"  - 用户ID: {self.user_id}")
                return self.user_id
            else:
                raise Exception(f"未找到用户ID，响应: {result}")
        except Exception as e:
            print(f"✗ 步骤5: 查询用户信息失败: {e}")
            raise

    def step6_recharge_user(self):
        """步骤6: 为用户充值"""
        url = "https://sea2admin.amigosqat.com/cdb/dzuser/user/straightBuckle"

        payload = {
            "money": "20000",
            "type": 1,
            "uid": self.user_id,
            "remark": ""
        }

        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "authorization": self.admin_token,
            "x-safe-password": self.step3_generate_google_code("JOWH72QSNE2SQVOH")
        }

        try:
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            print(f"✓ 步骤6: 充值成功")
            print(f"  - 金额: 20000")
            print(f"  - 响应: {result}")
            return result
        except Exception as e:
            print(f"✗ 步骤6: 充值失败: {e}")
            raise

    def step7_update_auth_yaml(self):
        """步骤7: 更新auth.yaml文件"""
        auth_yaml_path = current_dir / "core" / "auth_yaml" / "like_bofa_h5.yaml"

        try:
            # 读取现有的auth.yaml文件内容
            with open(auth_yaml_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 将手机号转换为数字格式（去除可能的空格和特殊字符）
            phone_number = self.phone.replace(' ', '').replace('-', '')

            # 使用正则表达式替换，保持原有格式和注释
            import re

            # 替换 tk 部分的 account 字段（保持缩进和格式）
            content = re.sub(
                r'(\s+account:\s+)\d+',
                rf'\g<1>{phone_number}',
                content,
                count=1
            )

            # 替换 bearer_token 部分的 username 字段（保持缩进和格式）
            content = re.sub(
                r'(\s+username:\s+)\d+',
                rf'\g<1>{phone_number}',
                content,
                count=1
            )

            # 写回文件，保持原有格式
            with open(auth_yaml_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✓ 步骤7: 更新auth.yaml文件成功")
            print(f"  - 文件路径: {auth_yaml_path}")
            print(f"  - 更新账号: {phone_number}")
            return True
        except Exception as e:
            print(f"✗ 步骤7: 更新auth.yaml文件失败: {e}")
            raise

    def run(self):
        """执行完整流程"""
        print("=" * 60)
        print("开始执行自动注册和充值流程")
        print("=" * 60)

        try:
            # 步骤1: 生成随机手机号
            self.step1_generate_phone()

            # 步骤2: 注册用户
            self.step2_register_user()

            # 步骤3: 生成谷歌验证码
            google_code = self.step3_generate_google_code()

            # 步骤4: 管理员登录
            self.step4_admin_login(google_code)

            # 步骤5: 查询用户ID
            self.step5_get_user_id()

            # 步骤6: 充值
            self.step6_recharge_user()

            # 步骤7: 更新auth.yaml
            self.step7_update_auth_yaml()

            print("=" * 60)
            print("✓ 所有步骤执行成功！")
            print(f"  - 注册手机号: {self.phone}")
            print(f"  - 用户ID: {self.user_id}")
            print(f"  - 充值金额: 20000")
            print("=" * 60)

            return True
        except Exception as e:
            print("=" * 60)
            print(f"✗ 执行失败: {e}")
            print("=" * 60)
            return False


def main():
    """主函数"""
    automation = AutoRegisterAndRecharge()
    success = automation.run()
    sys.exit(0 if success else 1)

def main():
    automation = AutoRegisterAndRecharge()
    success = automation.run()
    return success


if __name__ == "__main__":
    main()
