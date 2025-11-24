# 自动注册功能说明

## 问题说明

自动注册功能在运行时遇到了图片验证码错误 `WRONG_VALIDATION_IMG_CODE`。

## 原因

注册接口需要以下参数：
- `validateCode`: 图片验证码
- `uuid`: 验证码的 UUID

但是当前代码中这两个字段都是空的，导致注册失败。

## 解决方案

### 方案 1：禁用自动注册（默认）✅

**已实现！** 现在自动注册功能默认禁用，你可以直接运行测试：

```bash
python httpseeker/cli.py --auth httpseeker/core/auth_yaml/Dz_like_bofa_admin.yaml --env httpseeker/core/run_env/Dz_like_bofa_admin.env --conf_toml httpseeker/core/conf_toml/Dz_like_bofa_admin.toml --run
```

### 方案 2：启用自动注册（需要修复验证码问题）

如果你需要启用自动注册功能，需要先解决图片验证码问题：

#### 选项 A：使用不需要验证码的测试接口

如果后端提供了测试环境专用的注册接口（不需要验证码），修改 `auto_register_and_recharge.py` 中的 URL：

```python
# 修改 step2_register_user 函数中的 URL
url = "https://bofa.amigosqat.com/cdb/api/auth/test_reg"  # 测试专用接口
```

#### 选项 B：实现图片验证码自动识别

1. 先获取验证码图片和 UUID：

```python
def get_captcha(self):
    """获取图片验证码"""
    url = "https://bofa.amigosqat.com/cdb/api/auth/captcha"
    response = self.session.get(url)
    result = response.json()

    uuid = result['data']['uuid']
    img_base64 = result['data']['img']

    return uuid, img_base64
```

2. 使用 OCR 或第三方验证码识别服务识别验证码

3. 在注册时使用获取到的验证码：

```python
uuid, img_base64 = self.get_captcha()
code = recognize_captcha(img_base64)  # 识别验证码

payload = {
    "account": self.phone,
    "validateCode": code,
    "uuid": uuid,
    # ... 其他字段
}
```

#### 选项 C：联系后端关闭验证码

联系后端开发人员，在测试环境中关闭图片验证码验证。

#### 选项 D：手动注册测试账号

1. 手动注册一个测试账号
2. 更新 `auth.yaml` 文件中的账号信息
3. 不使用自动注册功能

## 如何启用自动注册

修复验证码问题后，可以通过环境变量启用：

```bash
# 方式 1：设置环境变量
export ENABLE_AUTO_REGISTER=true
python httpseeker/cli.py --run

# 方式 2：在命令中指定
ENABLE_AUTO_REGISTER=true python httpseeker/cli.py --run
```

## 当前修复

1. ✅ 修复了注册逻辑，会正确检查 API 返回结果
2. ✅ 创建了缺失的 `yaml_report` 目录
3. ✅ 让自动注册功能变成可选的，默认禁用

## 运行测试

现在你可以直接运行测试，不会再遇到自动注册失败的问题：

```bash
cd /Users/makino/Desktop/code/HttpSeek

# 激活虚拟环境（如果需要）
source .venv/bin/activate

# 运行测试
python httpseeker/cli.py \
  --auth httpseeker/core/auth_yaml/Dz_like_bofa_admin.yaml \
  --env httpseeker/core/run_env/Dz_like_bofa_admin.env \
  --conf_toml httpseeker/core/conf_toml/Dz_like_bofa_admin.toml \
  --run
```

## 相关文件

- `httpseeker/auto_register_and_recharge.py` - 自动注册逻辑
- `httpseeker/conftest.py` - pytest 配置，控制是否启用自动注册
- `httpseeker/core/auth_yaml/Dz_like_bofa_h5.yaml` - 认证配置文件

## 注意事项

1. 如果不需要每次运行都注册新用户，建议禁用自动注册功能
2. 如果需要自动注册，必须先解决图片验证码问题
3. 确保 `yaml_report` 目录存在（已自动创建）
