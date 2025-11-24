# Telegram Notifier 功能说明

## 核心功能

### 1. 自动发送测试报告到 Telegram ✅
- 支持测试结果通知（通过/失败）
- 显示详细的测试统计信息（通过、失败、错误、跳过）
- 包含测试开始时间和执行耗时
- 提供可点击的 Allure 报告链接

### 2. Jenkins 环境自动获取 🆕
**这是最重要的新功能！**

在 Jenkins 环境中运行时，自动从环境变量获取配置：

| 配置项 | Jenkins 环境变量 | 说明 |
|--------|-----------------|------|
| `project_name` | `JOB_NAME` | 自动使用 Jenkins 项目名称 |
| `jenkins_url` | `BUILD_URL` | 自动生成 Allure 报告地址 |

**优势：**
- ✅ 同一个配置文件可以在不同的 Jenkins 项目中复用
- ✅ 不需要为每个项目单独维护配置文件
- ✅ 在本地测试时使用配置文件的默认值
- ✅ 在 Jenkins 中自动使用正确的项目信息

**示例：**

```python
# Jenkins 环境变量：
# JOB_NAME = "Dz_Like_bofa_h5"
# BUILD_URL = "http://47.76.165.189:8080/job/Dz_Like_bofa_h5/125/"

# 自动生成的配置：
# project_name = "Dz_Like_bofa_h5"
# jenkins_url = "http://47.76.165.189:8080/job/Dz_Like_bofa_h5/allure/"
```

### 3. 消息模板与原版完全一致 ✅
发送的消息格式：

```
❌ FAIL ❌
Dz_like_bofa_h5接口自动化测试报告
👤 测试人员: Rookie
✅ 通过用例: 44
🔧 失败用例: 5
❌ 错误用例: 0
⚠️ 跳过用例: 0
⌛ 开始时间: 2025-11-20 15:12:40
⏱️ 执行耗时: 00:00:23
➡️ 查看详情
```

### 4. 多种使用方式 ✅

#### 方式 1：命令行
```bash
# 发送测试报告
python -m telegram_notifier.cli --report-file report.json

# 发送自定义消息
python -m telegram_notifier.cli --message "测试完成 ✅"
```

#### 方式 2：Python API
```python
from telegram_notifier import send_notification

report_data = {
    'result': 'Success',
    'passed': 10,
    'failed': 0,
    'error': 0,
    'skipped': 0,
    'started_time': '2024-01-01 10:00:00',
    'elapsed': '5.2s'
}

send_notification(report_data)
```

#### 方式 3：集成到现有项目
```python
import sys
sys.path.append('/path/to/telegram_notifier')
from telegram_notifier import send_notification

# 在测试结束后调用
send_notification(test_result, config_path='/path/to/config.toml')
```

### 5. 独立运行 ✅
- 不依赖原项目的任何模块
- 可以复制到任何地方使用
- 只需要 Python 和少量依赖包（requests, tomli）

### 6. 代理支持 ✅
支持 HTTP/HTTPS 代理配置，方便在受限网络环境中使用：

```toml
[telegram.proxies]
http = "http://proxy.example.com:8080"
https = "https://proxy.example.com:8080"
```

### 7. 灵活配置 ✅
- 支持 TOML 配置文件
- 支持自定义配置文件路径
- Jenkins 环境变量自动覆盖配置

## 技术特性

### 安全性
- Bot Token 和 Chat ID 存储在配置文件中
- 支持敏感信息环境变量配置
- 完整的异常处理和错误提示

### 兼容性
- Python 3.8+
- 兼容 Windows/Linux/macOS
- 支持 Python 3.11+ 原生 tomllib

### 可靠性
- HTTP 状态码检查
- Telegram API 返回结果验证
- 详细的错误日志输出
- 网络超时保护（30秒）

## 测试覆盖

提供多个测试脚本：

1. **test_notifier.py** - 基本功能测试
   - 测试发送报告
   - 测试发送自定义消息

2. **test_jenkins_env.py** - Jenkins 环境变量测试
   - 测试 JOB_NAME 自动获取
   - 测试 BUILD_URL 自动转换
   - 测试非 Jenkins 环境回退
   - 测试 URL 生成逻辑

3. **integration_example.py** - 集成示例
   - 5 种不同的集成方式
   - 包含实际代码示例

## 文档完善

提供完整的文档：

1. **README.md** - 完整使用文档
2. **QUICKSTART.md** - 5 分钟快速上手指南
3. **CHANGELOG.md** - 详细的更新日志和配置说明
4. **FEATURES.md** - 本文件，功能特性说明

## 与原项目的关系

- ✅ 已禁用原项目中的自动 Telegram 推送
- ✅ 保留了原有代码（注释形式），方便恢复
- ✅ 消息格式与原版完全一致
- ✅ 可以轻松集成回原项目

## 未来扩展可能

- [ ] 支持发送图片附件
- [ ] 支持发送文件附件
- [ ] 支持自定义消息模板
- [ ] 支持多个接收者
- [ ] 支持消息优先级
- [ ] 支持静音模式

## 总结

这是一个功能完整、独立运行的 Telegram 消息推送模块，特别适合：

1. ✅ 在 Jenkins CI/CD 环境中自动发送测试报告
2. ✅ 多个项目共享同一套推送配置
3. ✅ 需要灵活集成到各种测试框架
4. ✅ 需要自定义消息通知的场景

最大的亮点是 **Jenkins 环境变量自动获取功能**，极大简化了多项目配置管理！
