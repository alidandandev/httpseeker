# 快速开始指南

## 5 分钟快速上手

### 第 1 步：创建 Telegram Bot

1. 在 Telegram 中搜索 `@BotFather`
2. 发送命令 `/newbot`
3. 按提示输入 bot 名称和用户名
4. 复制获得的 Bot Token（格式：`123456789:ABCdefGHI...`）

### 第 2 步：获取 Chat ID

**方法 1（推荐）：**
1. 向你创建的 bot 发送任意消息（例如：`/start`）
2. 在浏览器打开：`https://api.telegram.org/bot<你的Bot Token>/getUpdates`
3. 在返回的 JSON 中找到 `"chat":{"id":123456789}`，这个数字就是你的 Chat ID

**方法 2：**
1. 在 Telegram 搜索 `@userinfobot`
2. 发送任意消息，会返回你的 User ID（即 Chat ID）

### 第 3 步：配置

编辑 `config.toml` 文件，填入你的信息：

```toml
[telegram]
bot_token = "123456789:ABCdefGHI..."  # 替换为你的 Bot Token
chat_id = "123456789"                 # 替换为你的 Chat ID
send = true

[report]
project_name = "我的测试项目"          # 替换为你的项目名
tester_name = "张三"                  # 替换为你的名字
jenkins_url = "http://your-url/"      # 替换为你的报告链接（可选）
```

**💡 重要提示：**

如果你在 Jenkins 环境中运行，以下配置会**自动获取**，无需手动配置：
- `project_name` - 自动从 Jenkins 环境变量 `JOB_NAME` 获取
- `jenkins_url` - 自动从 Jenkins 环境变量 `BUILD_URL` 生成

这意味着同一个配置文件可以在不同的 Jenkins 项目中复用！

### 第 4 步：安装依赖

```bash
cd telegram_notifier
pip install -r requirements.txt
```

### 第 5 步：测试

#### 方式 1：使用测试脚本

```bash
python test_notifier.py
```

#### 方式 2：命令行测试

```bash
# 测试发送消息
python -m telegram_notifier.cli --message "测试消息"

# 测试发送报告
python -m telegram_notifier.cli --report-file example_report.json
```

#### 方式 3：Python 代码测试

创建 `test.py`：

```python
from telegram_notifier import send_message

# 发送一条测试消息
send_message("你好！这是一条测试消息 ✅")
```

运行：
```bash
python test.py
```

## 常见问题

### Q1: 收不到消息？

检查清单：
- ✅ 确认已向 bot 发送过至少一条消息
- ✅ Bot Token 和 Chat ID 都正确填写
- ✅ `config.toml` 中 `send = true`
- ✅ 网络能访问 Telegram（国内可能需要代理）

### Q2: 如何在群组中使用？

1. 将 bot 添加到群组
2. 在群组中发送任意消息（例如：`@你的bot /start`）
3. 访问 `https://api.telegram.org/bot<Bot Token>/getUpdates`
4. 找到群组的 Chat ID（通常是负数，如 `-123456789`）
5. 在 `config.toml` 中填入群组的 Chat ID

### Q3: 如何使用代理？

在 `config.toml` 中配置代理：

```toml
[telegram.proxies]
http = "http://127.0.0.1:7890"
https = "http://127.0.0.1:7890"
```

### Q4: 如何在原项目中集成？

在你的 Python 脚本中：

```python
# 方式 1：添加到 Python 路径
import sys
sys.path.append('/path/to/telegram_notifier所在目录')

from telegram_notifier import send_notification

# 发送报告
report_data = {
    'result': 'Success',
    'passed': 10,
    'failed': 0,
    'error': 0,
    'skipped': 0,
    'started_time': '2024-01-01 10:00:00',
    'elapsed': '5.2s'
}

send_notification(report_data, config_path='/path/to/config.toml')
```

## 下一步

- 查看 [README.md](README.md) 了解完整功能
- 查看 [test_notifier.py](test_notifier.py) 了解更多使用示例
- 根据你的需求修改 `config.toml` 配置

祝使用愉快！
