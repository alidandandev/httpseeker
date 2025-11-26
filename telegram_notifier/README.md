# Telegram Notifier

独立的 Telegram 消息推送模块，支持测试报告推送和自定义消息推送。

## 功能特性

- 发送测试报告到 Telegram
- 发送自定义消息到 Telegram
- 支持 Markdown 和 HTML 格式
- 支持代理配置
- 命令行和 Python API 两种使用方式
- 独立运行，无需依赖其他项目模块

## 目录结构

```
telegram_notifier/
├── __init__.py          # 模块初始化
├── __main__.py          # 支持 python -m 运行
├── config.py            # 配置管理
├── notifier.py          # 核心推送功能
├── cli.py               # 命令行接口
├── config.toml          # 配置文件示例
├── requirements.txt     # 依赖包
└── README.md            # 使用说明
```

## 安装

### 1. 安装依赖

```bash
cd telegram_notifier
pip install -r requirements.txt
```

### 2. 配置 Telegram Bot

#### 创建 Telegram Bot

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 创建新 bot
3. 按提示设置 bot 名称和用户名
4. 获取 Bot Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

#### 获取 Chat ID

有两种方式获取 Chat ID：

**方式 1：使用 Bot API**

1. 向你的 bot 发送一条消息
2. 访问：`https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. 在返回的 JSON 中找到 `chat.id` 字段

**方式 2：使用第三方 Bot**

1. 搜索 `@userinfobot`
2. 发送任意消息获取你的 Chat ID

### 3. 配置文件

编辑 `config.toml` 文件：

```toml
# Telegram Bot 配置
[telegram]
# Telegram Bot Token (从 @BotFather 获取)
bot_token = "your-bot-token-here"

# Telegram Chat ID (个人ID或群组ID)
chat_id = "your-chat-id-here"

# 是否启用推送
send = true

# 代理配置 (如果需要)
[telegram.proxies]
http = ""
https = ""

# 报告配置
[report]
# 项目名称
project_name = "接口自动化测试"

# 测试人员名称
tester_name = "Tester"

# Jenkins 或报告详情链接
jenkins_url = "http://your-jenkins-url/allure/"
```

**重要提示：Jenkins 环境自动获取**

当在 Jenkins 环境中运行时，模块会自动从环境变量获取配置：
- `project_name` - 自动从 `JOB_NAME` 环境变量获取
- `jenkins_url` - 自动从 `BUILD_URL` 环境变量生成（格式：`http://host/job/jobname/allure/`）

这意味着在 Jenkins 中运行时，这两个配置会被自动覆盖，无需手动修改配置文件。

## 使用方法

### 方式 1：命令行使用

#### 发送测试报告

```bash
# 直接传递 JSON 数据
python -m telegram_notifier.cli --report '{"result": "Success", "passed": 10, "failed": 0, "error": 0, "skipped": 0, "started_time": "2024-01-01 10:00:00", "elapsed": "5.2s"}'

# 从 JSON 文件读取
python -m telegram_notifier.cli --report-file report.json
```

#### 发送自定义消息

```bash
# 发送 Markdown 格式消息
python -m telegram_notifier.cli --message "测试完成！\n*状态*: 通过"

# 发送 HTML 格式消息
python -m telegram_notifier.cli --message "<b>测试完成</b>" --parse-mode HTML
```

#### 使用自定义配置文件

```bash
python -m telegram_notifier.cli --config /path/to/config.toml --message "Hello"
```

### 方式 2：Python API 使用

#### 发送测试报告

```python
from telegram_notifier import send_notification

# 准备测试报告数据
report_data = {
    'result': 'Success',  # 或 'Failed'
    'passed': 10,
    'failed': 0,
    'error': 0,
    'skipped': 0,
    'started_time': '2024-01-01 10:00:00',
    'elapsed': '5.2s'
}

# 发送通知（使用默认配置）
success = send_notification(report_data)

# 使用自定义配置文件
success = send_notification(report_data, config_path='/path/to/config.toml')
```

#### 发送自定义消息

```python
from telegram_notifier import send_message

# 发送 Markdown 格式消息
send_message("*测试完成！*\n\n✅ 所有用例通过")

# 发送 HTML 格式消息
send_message("<b>测试完成</b>", parse_mode='HTML')
```

#### 高级用法

```python
from telegram_notifier import load_config, TelegramNotifier

# 加载配置
config = load_config('/path/to/config.toml')

# 创建推送器
notifier = TelegramNotifier(config)

# 发送测试报告
report_data = {
    'result': 'Success',
    'passed': 10,
    'failed': 0,
    'error': 0,
    'skipped': 0,
    'started_time': '2024-01-01 10:00:00',
    'elapsed': '5.2s'
}
notifier.send_test_report(report_data)

# 发送自定义消息
notifier.send_custom_message("自定义消息内容")
```

## 集成到现有项目

### 在 HttpSeeker 项目中使用

在 `httpseeker/run.py` 中替换原有的 Telegram 推送：

```python
# 原来的方式
from httpseeker.utils.send_report.telegram import Telegram
if httpseeker_config.TELEGRAM_SEND:
    Telegram(test_result).send()

# 新的独立模块方式
import sys
sys.path.append('/path/to/telegram_notifier')
from telegram_notifier import send_notification

if httpseeker_config.TELEGRAM_SEND:
    send_notification(test_result, config_path='/path/to/config.toml')
```

### 在其他项目中使用

```python
# 方式 1：将 telegram_notifier 目录复制到项目中
from telegram_notifier import send_notification

# 方式 2：将 telegram_notifier 添加到 Python 路径
import sys
sys.path.append('/path/to/telegram_notifier')
from telegram_notifier import send_notification
```

## 测试报告数据格式

测试报告 JSON 数据格式：

```json
{
    "result": "Success",          // 或 "Failed"
    "passed": 10,                 // 通过用例数
    "failed": 0,                  // 失败用例数
    "error": 0,                   // 错误用例数
    "skipped": 0,                 // 跳过用例数
    "started_time": "2024-01-01 10:00:00",  // 开始时间
    "elapsed": "5.2s"             // 执行耗时
}
```

## 消息格式

### Markdown 格式

```markdown
*粗体*
_斜体_
[链接文本](URL)
`代码`
```

### HTML 格式

```html
<b>粗体</b>
<i>斜体</i>
<a href="URL">链接文本</a>
<code>代码</code>
```

## 代理配置

如果需要使用代理访问 Telegram API，在 `config.toml` 中配置：

```toml
[telegram.proxies]
http = "http://proxy.example.com:8080"
https = "https://proxy.example.com:8080"
```

## 故障排查

### 1. Bot Token 无效

错误：`Unauthorized`

解决：检查 `bot_token` 是否正确，确保从 @BotFather 获取的 token 完整复制

### 2. Chat ID 无效

错误：`Bad Request: chat not found`

解决：
- 确保已向 bot 发送过消息
- 检查 Chat ID 格式（个人 ID 通常是正数，群组 ID 通常是负数）
- 群组 Chat ID 前面需要加 `-` 号

### 3. 网络连接问题

错误：`Connection timeout` 或 `Connection refused`

解决：
- 检查网络连接
- 如果在中国大陆，可能需要配置代理
- 检查防火墙设置

### 4. 消息格式错误

错误：`Bad Request: can't parse entities`

解决：
- 检查 Markdown/HTML 格式是否正确
- 特殊字符需要转义
- 链接格式：`[文本](URL)` (Markdown) 或 `<a href="URL">文本</a>` (HTML)

## 依赖项

- Python >= 3.8
- requests >= 2.28.0
- tomli >= 2.0.0 (仅 Python < 3.11)

## 版本历史

### v1.0.0 (2024-01-01)

- 初始版本
- 支持测试报告推送
- 支持自定义消息推送
- 支持命令行和 Python API
- 支持代理配置

## License

MIT License

## 联系方式

如有问题或建议，请联系项目维护者。
