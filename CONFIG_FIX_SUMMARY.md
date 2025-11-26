# 配置文件加载问题修复总结

## 问题描述

运行命令时指定了 `Dz_like_bofa_admin` 的配置文件，但实际运行的是 `Dz_like_bofa_h5` 的用例：

```bash
python httpseeker/cli.py \
  --auth httpseeker/core/auth_yaml/Dz_like_bofa_admin.yaml \
  --env httpseeker/core/run_env/Dz_like_bofa_admin.env \
  --conf_toml httpseeker/core/conf_toml/Dz_like_bofa_admin.toml \
  --run
```

## 根本原因

### 问题 1：配置加载时机错误

**原因：**
1. `httpseeker/run.py:19` 在导入时就初始化了 `httpseeker_config`
2. `run()` 函数在第 235-238 行才设置环境变量
3. 配置使用了 `@lru_cache` 缓存，即使设置环境变量也不会重新加载

**结果：** 无论传什么配置文件，都会使用默认配置 `Dz_like_bofa_h5.toml`

### 问题 2：配置文件语法错误

`Dz_like_bofa_admin.toml` 第 10 行的 `jenkins_url` 值被截断：
```toml
jenkins_url = 'https://foryourselfz_
```

导致 TOML 解析错误：`newline in string found at line 10 column 37`

### 问题 3：配置文件缺少必需字段

`Dz_like_bofa_admin.toml` 缺少 `[telegram]` 配置段。

## 修复内容

### 修复 1：配置重新加载机制 ✅

**文件：** `httpseeker/run.py:240-253`

在设置环境变量后，清除缓存并重新加载配置：

```python
# 重新加载配置（清除缓存后重新导入）
if conf_path is not None or global_env is not None or auth_path is not None:
    from httpseeker.core.get_conf import cache_httpseeker_config
    cache_httpseeker_config.cache_clear()
    # 重新导入配置模块以获取最新配置
    import importlib
    import httpseeker.core.get_conf as get_conf_module
    import httpseeker.core.path_conf as path_conf_module
    importlib.reload(get_conf_module)
    importlib.reload(path_conf_module)
    # 更新全局引用
    global httpseeker_config, httpseeker_path
    from httpseeker.core.get_conf import httpseeker_config
    from httpseeker.core.path_conf import httpseeker_path
```

### 修复 2：修复配置文件语法错误 ✅

**文件：** `httpseeker/core/conf_toml/Dz_like_bofa_admin.toml:10`

修复前：
```toml
jenkins_url = 'https://foryourselfz_
```

修复后：
```toml
jenkins_url = 'http://47.76.165.189:8080/job/Dz_Like_bofa_admin/allure/'
```

### 修复 3：补充缺失的 Telegram 配置 ✅

**文件：** `httpseeker/core/conf_toml/Dz_like_bofa_admin.toml:60-66`

添加了完整的 Telegram 配置：
```toml
# Telegram
[telegram]
bot_token = '6968270418:AAGlX7tNpfnIuueB2hAssZWzwuNCMjR6ryE'
chat_id = '-4781359846'
proxies.http = ''
proxies.https = ''
send = true
```

### 额外改进：显示当前项目名 ✅

在启动时显示当前加载的项目名，方便确认：

```python
log.info(f'📋 当前项目: {httpseeker_config.PROJECT_NAME}')
```

## 验证测试

测试配置加载是否正确：

```bash
python -c "
import os
os.environ['HTTPSEEKER_CONF_PATH'] = 'httpseeker/core/conf_toml/Dz_like_bofa_admin.toml'

from httpseeker.core.get_conf import cache_httpseeker_config
cache_httpseeker_config.cache_clear()

import importlib
import httpseeker.core.get_conf as get_conf_module
importlib.reload(get_conf_module)

from httpseeker.core.get_conf import httpseeker_config
print(f'项目名: {httpseeker_config.PROJECT_NAME}')
"
```

**预期输出：** `项目名: Dz_like_bofa_admin`

## 现在可以正常运行

```bash
# 运行 Dz_like_bofa_admin 项目
python httpseeker/cli.py \
  --auth httpseeker/core/auth_yaml/Dz_like_bofa_admin.yaml \
  --env httpseeker/core/run_env/Dz_like_bofa_admin.env \
  --conf_toml httpseeker/core/conf_toml/Dz_like_bofa_admin.toml \
  --run
```

应该会看到：
```
📋 当前项目: Dz_like_bofa_admin
```

然后运行 `httpseeker/testcases/Dz_like_bofa_admin/` 目录下的测试用例。

## 修复的文件列表

1. ✅ `httpseeker/run.py` - 添加配置重新加载逻辑
2. ✅ `httpseeker/core/conf_toml/Dz_like_bofa_admin.toml` - 修复语法错误并补充配置
3. ✅ `httpseeker/conftest.py` - 让自动注册功能可选（之前的修复）
4. ✅ `httpseeker/auto_register_and_recharge.py` - 修复注册逻辑（之前的修复）
5. ✅ 创建了 `httpseeker/report/yaml_report/` 目录（之前的修复）

## 相关问题修复

同时修复了以下问题：
- ✅ 自动注册失败导致测试无法运行（已禁用）
- ✅ yaml_report 目录不存在
- ✅ 配置文件加载时机问题

## 注意事项

1. **使用正确的配置文件路径**
   - 使用相对路径或绝对路径
   - 确保文件存在且格式正确

2. **查看启动日志**
   - 检查 `📋 当前项目:` 确认加载的是正确的项目

3. **配置文件要求**
   - TOML 格式必须正确
   - 必须包含所有必需的配置段（telegram、request 等）

4. **测试用例目录**
   - 确保 `httpseeker/testcases/{PROJECT_NAME}/` 目录存在
   - 目录名必须与配置文件中的 `project.name` 一致

## 如果还有问题

如果运行后仍然执行错误的项目用例，请检查：

1. 启动日志中的项目名是否正确
2. 配置文件路径是否正确
3. 测试用例目录是否存在
4. 配置文件是否有语法错误

使用以下命令测试配置文件语法：
```bash
python -c "from httpseeker.common.toml_handler import read_toml; print(read_toml('httpseeker/core/conf_toml', 'Dz_like_bofa_admin.toml'))"
```
