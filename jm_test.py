from httpseeker.utils.encryption_filter import EncryptionFilter
import json


# 全局加密密钥（32字节）
ENCRYPTION_KEY = "your-32-byte-secure-aes-key-1234"


def encrypt_request(request_body):
    """
    加密请求体

    Args:
        request_body: 请求体数据（dict 或 str）

    Returns:
        dict: 加密后的请求体，格式为 {"data": "加密字符串"}
    """
    print("=" * 70)
    print("🔐 加密请求")
    print("=" * 70)
    print(f"原始请求:\n{json.dumps(request_body, ensure_ascii=False, indent=2)}")

    encryption_filter = EncryptionFilter(encryption_enabled=True, encryption_key=ENCRYPTION_KEY)
    encrypted_body, headers = encryption_filter.encrypt_request_body(request_body)

    print(f"\n加密后的请求:\n{json.dumps(encrypted_body, ensure_ascii=False, indent=2)}")
    print("=" * 70 + "\n")
    return encrypted_body


def decrypt_response(response_data):
    """
    解密响应数据

    Args:
        response_data: 响应数据（dict），包含加密的data字段

    Returns:
        dict: 解密后的响应数据
    """
    print("=" * 70)
    print("🔓 解密响应")
    print("=" * 70)
    print(f"加密的响应:\n{json.dumps(response_data, ensure_ascii=False, indent=2)}")

    encryption_filter = EncryptionFilter(encryption_enabled=True, encryption_key=ENCRYPTION_KEY)
    decrypted_data = encryption_filter.decrypt_response_data(response_data)

    print(f"\n解密后的响应:\n{json.dumps(decrypted_data, ensure_ascii=False, indent=2)}")
    print("=" * 70 + "\n")
    return decrypted_data


# 使用示例
if __name__ == "__main__":
    # 加密例子
    data = {"data":"KCv3eOLquxV4LTD3eiKusVEf7GnlMJANfJfSxPBAwc89Q57hrroAoaveTWkeYJGTC0mriLEX+l3XYYooXS0pm1jbkmPEJrfeypcH+ggCd1U="}
    decrypt_response(data)
    data = {"data":"tGTC54e29uj506drsnOpYyBRFhRH0LKw77hq8PTkTu0rOiWQie34Lp22y3DfOHKJd1zyIbmGGpbSC22ygcuJkxu28mQMltNngmMVZS/sqO8="}
    decrypt_response(data)
    data = {"data":"Oxcwg+0E4Ycm5k0FKon2LBKH+e0tx7uUB2QT9t08tb/T/a6+XKaP7c4n+6V3knRiZo3dQIPREFF9o5w5OtkS2jNTwrDCjWbvjBMoU+5Rmv6kf2KrLn6zNln67xGoP4cM"}
    decrypt_response(data)
    # data = {
    # "code": 20000,
    # "msg": "success",
    # "data": "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",
    # "success": "true"
    # }
    # decrypt_response(data)


