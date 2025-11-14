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
    data = {"data":"3mJdmdPNuwE9FCZaY7LTgIzoOxGCN6hQ+LO2/M3JY5FwsZcnkfxwLyAwfN9KfrMymQ50MWWepzx16Z4PHBHesJeamKXK4ESiwJiW5nVDsGNHJ/MbRKusV5Xnbp9EDi3pUWlWbOk7IEmwpKlo4TqgQ93H2duGUDjLzr6ecf2EYGYSbzrNFeGmsvMrVRfm9QjHVV1iDZgXAZUpGqft5imsBuA5hHq2WnKDBOAiPGDJbW1j8PGIj3SLD/CNtTIxiV0pRxdNvxQ+dZRNMIKeXBLrPQMlf3SlIjnZJKnXyAI96cTg+SFDzDZs4XpHCEsT+ubS7IVFFAoYMnpC44b592cG8eap9JkD0EoPqvnZ6bVBRkCkih+ScPjqTGOetw7+piBtP5HCy3lFd/GaA53i1wDSOplBE4LONFTvdAAhBi989wJm5RZEyq7bGbluEo+omVM7+196H2tlvmqDRRB8Ku8+3g=="}
    decrypt_response(data)
    data = {"data":"tGTC54e29uj506drsnOpYyBRFhRH0LKw77hq8PTkTu0rOiWQie34Lp22y3DfOHKJd1zyIbmGGpbSC22ygcuJkxu28mQMltNngmMVZS/sqO8="}
    decrypt_response(data)
    data = {"data":"Oxcwg+0E4Ycm5k0FKon2LBKH+e0tx7uUB2QT9t08tb/T/a6+XKaP7c4n+6V3knRiZo3dQIPREFF9o5w5OtkS2jNTwrDCjWbvjBMoU+5Rmv6kf2KrLn6zNln67xGoP4cM"}
    decrypt_response(data)


