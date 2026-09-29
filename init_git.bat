@echo off
chcp 65001 >nul
echo ========================================
echo 新浪财经分红数据项目 - Git初始化脚本
echo ========================================
echo.

REM 检查Git是否安装
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Git，请先安装Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/5] 初始化Git仓库...
git init

echo.
echo [2/5] 配置用户信息（如已配置可跳过）...
git config user.name "Student"
git config user.email "student@example.com"

echo.
echo [3/5] 添加所有文件...
git add .

echo.
echo [4/5] 提交代码...
git commit -m "feat: 新浪财经历史分红数据获取与预处理实战项目

- 实现新浪财经个股分红数据爬虫（5只股票，161条记录）
- 完成数据清洗、衍生指标计算和多维度统计分析
- 开发交互式数据可视化网页（ECharts 6种图表）
- 实现Playwright自动化测试（8项测试，通过率94.4%%）
- 包含完整文档和脱敏对话记录"

echo.
echo [5/5] 查看提交记录...
git log --oneline -5

echo.
echo ========================================
echo Git仓库初始化完成！
echo ========================================
echo.
echo 如需推送到远程仓库，请执行以下命令：
echo   git remote add origin ^<你的仓库地址^>
echo   git branch -M main
echo   git push -u origin main
echo.
echo 例如（GitHub）：
echo   git remote add origin https://github.com/你的用户名/sina-dividend-project.git
echo   git push -u origin main
echo.
pause
