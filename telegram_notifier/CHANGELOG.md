# 更新日志

## 2024-11-23 - 消息模板更新及 Jenkins 自动获取功能

### 修改内容

1. **消息模板已与原始格式完全一致**
   - 保留了原来的消息格式
   - 项目名称加粗显示：`*项目名接口自动化测试报告*`
   - "查看详情"链接使用 Markdown 格式：`[查看详情](URL)`

2. **配置文件已更新**
   - 填入了实际的 Bot Token 和 Chat ID
   - 项目名称：`Dz_like_bofa_h5`
   - 测试人员：`Rookie`
   - Jenkins URL：`http://47.76.165.189:8080/job/Dz_Like_bofa_h5/allure/`

3. **Jenkins 环境自动获取功能（新增）**
   - 支持从 `JOB_NAME` 环境变量自动获取项目名称
   - 支持从 `BUILD_URL` 环境变量自动生成 Allure 报告地址
   - 在 Jenkins 中运行时无需手动修改配置文件

4. **代码优化**
   - 修复了潜在的变量引用问题
   - 改进了异常处理逻辑

### 消息示例

发送的消息格式如下：

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

注：在 Telegram 中，"查看详情"会显示为可点击的链接，指向配置的 Jenkins Allure 报告地址。

### 如何使用

#### 方式 1：命令行测试

```bash
cd telegram_notifier

# 使用示例报告文件测试
python -m telegram_notifier.cli --report-file example_report.json

# 发送自定义消息
python -m telegram_notifier.cli --message "测试消息"
```

#### 方式 2：Python 代码调用

```python
import sys
sys.path.append('/Users/makino/Desktop/code/HttpSeek')
from telegram_notifier import send_notification

# 准备报告数据
report_data = {
    'result': 'Failed',
    'passed': 44,
    'failed': 5,
    'error': 0,
    'skipped': 0,
    'started_time': '2025-11-20 15:12:40',
    'elapsed': '00:00:23'
}

# 发送通知
config_path = '/Users/makino/Desktop/code/HttpSeek/telegram_notifier/config.toml'
send_notification(report_data, config_path=config_path)
```

#### 方式 3：集成到 HttpSeeker

如果想恢复自动推送功能，可以在 `httpseeker/run.py:148` 处取消注释并修改为：

```python
if httpseeker_config.TELEGRAM_SEND:
    import sys
    sys.path.append('/Users/makino/Desktop/code/HttpSeek')
    from telegram_notifier import send_notification

    config_path = '/Users/makino/Desktop/code/HttpSeek/telegram_notifier/config.toml'
    send_notification(test_result, config_path=config_path)
```

### 配置说明

所有配置在 `config.toml` 文件中：

- `telegram.bot_token`: Telegram Bot Token
- `telegram.chat_id`: 接收消息的 Chat ID
- `telegram.send`: 是否启用推送（true/false）
- `telegram.proxies`: 代理配置（如需要）
- `report.project_name`: 项目名称（Jenkins 环境中自动从 `JOB_NAME` 获取）
- `report.tester_name`: 测试人员名称
- `report.jenkins_url`: Jenkins Allure 报告地址（Jenkins 环境中自动从 `BUILD_URL` 生成）

### Jenkins 自动获取功能说明

当在 Jenkins 环境中运行时，模块会自动检测并使用以下环境变量：

1. **JOB_NAME**：Jenkins 项目名称
   - 示例值：`Dz_Like_bofa_h5`
   - 自动覆盖 `config.toml` 中的 `project_name`

2. **BUILD_URL**：当前构建的完整 URL
   - 示例值：`http://47.76.165.189:8080/job/Dz_Like_bofa_h5/125/`
   - 自动转换为：`http://47.76.165.189:8080/job/Dz_Like_bofa_h5/allure/`
   - 自动覆盖 `config.toml` 中的 `jenkins_url`

这样设计的好处：
- ✅ 同一个配置文件可以在不同的 Jenkins 项目中复用
- ✅ 不需要为每个项目单独维护配置文件
- ✅ 在本地测试时使用配置文件的默认值，在 Jenkins 中自动使用正确的项目信息

### 原项目修改

已在原项目中禁用了自动 Telegram 推送：

- `httpseeker/run.py:28` - 注释掉了 Telegram 的 import
- `httpseeker/run.py:148-150` - 注释掉了自动推送代码

如需恢复，参考上面的"方式 3"。
