@echo off
REM 显式设置控制台编码（兼容Jenkins子进程）
chcp 65001 > nul

REM 确保conda初始化路径正确（根据实际路径调整）
call C:\ProgramData\anaconda3\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 错误：conda初始化失败
    exit /b 1
)

REM 激活环境并验证
call conda activate api
if %errorlevel% neq 0 (
    echo 错误：激活conda环境失败
    exit /b 1
)

REM 设置Python输出编码（双重保障）
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

REM 安装项目
pip install -e .
if %errorlevel% neq 0 (
    echo 错误：项目安装失败
    exit /b 1
)

REM 运行测试（会自动生成allure原始数据到 httpseeker/report/allure_report）
python httpseeker/cli.py ^
    --env httpseeker/core/run_env/like_bofa_h5_test.env ^
    --conf_toml httpseeker/core/conf_toml/like_bofa_h5.toml ^
    --auth httpseeker/core/auth_yaml/like_bofa_h5.yaml ^
    --run

REM 检查allure原始数据是否生成
if not exist "httpseeker\report\allure_report" (
    echo 警告：Allure原始数据未生成
    exit /b 1
)

echo 测试完成，Allure原始数据已生成到: httpseeker\report\allure_report
echo 请在Jenkins中配置Allure插件来展示报告
