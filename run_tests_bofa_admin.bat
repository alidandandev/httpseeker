@echo off
REM ========================================
REM Jenkins自动化测试执行脚本
REM 解决Windows环境下中文乱码问题
REM ========================================

REM 第一步：设置控制台为UTF-8编码
chcp 65001 > nul 2>&1

REM 第二步：设置环境变量强制UTF-8编码
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8
set PYTHONUNBUFFERED=1
set PYTHONUTF8=1
set PYTEST_THEME=none

REM 第三步：设置Java编码（用于Allure）
set JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF-8

REM 第四步：初始化Conda
call C:\ProgramData\anaconda3\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Conda initialization failed
    exit /b 1
)

REM 第五步：激活虚拟环境
call conda activate api
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate conda environment
    exit /b 1
)

REM 第六步：安装项目
echo [INFO] Installing project...
pip install -e . >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Project installation failed
    exit /b 1
)

REM 第七步：运行测试
echo [INFO] Running tests...
python httpseeker/cli.py ^
    --conf_toml httpseeker/core/conf_toml/Dz_like_bofa_admin.toml ^
    --auth httpseeker/core/auth_yaml/Dz_like_bofa_admin.yaml ^
    --run

REM 第八步：检查测试结果
if not exist "httpseeker\report\allure_report" (
    echo [WARNING] Allure report data not generated
    exit /b 1
)

echo [SUCCESS] Tests completed
echo [INFO] Allure data: httpseeker\report\allure_report
echo [INFO] HTML report: httpseeker\report\html_report
exit /b 0
