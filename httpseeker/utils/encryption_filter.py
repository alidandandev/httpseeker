#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密解密过滤器
支持 AES-256-CBC 加密算法
"""
from __future__ import annotations

import base64
import json
import logging

from typing import Optional, Dict

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

logger = logging.getLogger(__name__)


class EncryptionFilter:
    """
    加密解密过滤器
    用于自动处理请求加密和响应解密
    """
    ALGORITHM = "AES/CBC/PKCS5Padding"
    DEFAULT_KEY = "your-32-byte-secure-aes-key-1234"
    IV_LENGTH = 16

    def __init__(self, encryption_enabled: bool = False, encryption_key: str = None):
        """
        初始化加密过滤器

        Args:
            encryption_enabled: 是否启用加密
            encryption_key: 加密密钥（32字节）
        """
        self.encryption_enabled = encryption_enabled
        self.encryption_key = (encryption_key or self.DEFAULT_KEY).encode('utf-8')

        if len(self.encryption_key) != 32:
            raise ValueError(f"AES密钥长度必须为32字节，当前: {len(self.encryption_key)}")

    def encrypt(self, plain_text: str) -> str:
        """
        加密字符串

        Args:
            plain_text: 明文字符串

        Returns:
            Base64编码的密文
        """
        try:
            iv = get_random_bytes(self.IV_LENGTH)
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            plain_bytes = plain_text.encode('utf-8')
            padded_data = pad(plain_bytes, AES.block_size)
            encrypted = cipher.encrypt(padded_data)
            combined = iv + encrypted
            return base64.b64encode(combined).decode('utf-8')
        except Exception as e:
            logger.error(f"加密失败: {e}")
            raise

    def decrypt(self, encrypted_data: str) -> str:
        """
        解密字符串

        Args:
            encrypted_data: Base64编码的密文

        Returns:
            解密后的明文字符串
        """
        try:
            decoded = base64.b64decode(encrypted_data)
            iv = decoded[:16]
            cipher_text = decoded[16:]
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(cipher_text)
            unpadded = unpad(decrypted, AES.block_size)
            return unpadded.decode('utf-8')
        except Exception as e:
            logger.error(f"解密失败: {e}")
            raise IOError(f"解密失败: {e}")

    def encrypt_request_body(self, body: any) -> tuple[str, Dict[str, str]]:
        """
        加密请求体

        Args:
            body: 请求体数据（dict或str）

        Returns:
            (加密后的请求体JSON字符串, 额外的请求头)
        """
        if not self.encryption_enabled:
            return body, {}

        try:
            # 转换为JSON字符串
            if isinstance(body, dict):
                body_str = json.dumps(body, ensure_ascii=False)
            else:
                body_str = str(body)

            # 加密数据
            encrypted_data = self.encrypt(body_str)

            # 构造加密请求体
            encrypted_body = {"data": encrypted_data}

            # 添加加密标识头
            extra_headers = {"X-Encrypted": "true"}

            logger.debug(f"请求体加密成功，原始长度: {len(body_str)}, 加密后长度: {len(encrypted_data)}")

            return encrypted_body, extra_headers

        except Exception as e:
            logger.error(f"请求体加密失败: {e}")
            raise

    def decrypt_response_data(self, response_json: dict) -> dict:
        """
        智能解密响应数据
        策略：
        1. 先尝试将整个响应体作为加密字符串解密
        2. 如果失败，则尝试解密响应中的 data 字段

        Args:
            response_json: 响应JSON数据

        Returns:
            解密后的响应数据
        """
        if not self.encryption_enabled:
            return response_json

        try:
            # 策略1: 尝试将整个响应体作为加密字符串解密
            # 如果整个响应就是一个包含加密字符串的简单结构
            if len(response_json) == 1 and isinstance(list(response_json.values())[0], str):
                encrypted_full_response = list(response_json.values())[0]
                try:
                    decrypted_full = self.decrypt(encrypted_full_response)
                    try:
                        # 尝试解析为JSON对象
                        decrypted_json = json.loads(decrypted_full)
                        logger.info("✓ 整个响应体解密成功，解析为JSON对象")
                        return decrypted_json
                    except json.JSONDecodeError:
                        # 不是JSON，返回原始响应
                        logger.debug("整个响应体解密后不是JSON，尝试其他策略")
                except Exception as e:
                    logger.debug(f"整个响应体解密失败，尝试其他策略: {e}")

            # 策略2: 检查响应中是否包含加密的data字段
            if "data" in response_json and isinstance(response_json["data"], str):
                encrypted_data = response_json["data"]

                # 尝试解密data字段
                try:
                    decrypted_data = self.decrypt(encrypted_data)

                    # 尝试将解密后的数据解析为JSON
                    try:
                        response_json["data"] = json.loads(decrypted_data)
                        logger.info("✓ 响应data字段解密成功，解析为JSON对象")
                    except json.JSONDecodeError:
                        # 不是JSON，保留为字符串（可能是token等）
                        response_json["data"] = decrypted_data
                        logger.info("✓ 响应data字段解密成功，保留为字符串")

                except Exception as e:
                    logger.warning(f"data字段解密失败，保留原始内容: {e}")

            return response_json

        except Exception as e:
            logger.error(f"响应数据解密失败: {e}")
            return response_json

    def is_encrypted_request(self, headers: Dict[str, str]) -> bool:
        """
        检查请求头中是否标识为加密请求

        Args:
            headers: 请求头字典

        Returns:
            是否为加密请求
        """
        encrypted_header = headers.get("X-Encrypted", "").lower()
        return encrypted_header == "true"
