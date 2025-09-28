@echo off
echo ========================================
echo 🚀 Interview Helper - 增强版启动脚本
echo ========================================

echo.
echo 📍 切换到后端目录...
cd backend

echo.
echo 🔧 检查Python环境...
python --version

echo.
echo 📦 检查依赖包...
pip list | findstr "fastapi uvicorn openai"

echo.
echo 🚀 启动后端服务器（带详细日志）...
echo.
echo 📊 现在你可以在后端命令行看到：
echo    - 简历上传状态
echo    - 技能匹配度计算过程
echo    - 经验匹配度计算过程
echo    - AI分析详细过程
echo.
echo 🌐 前端访问地址: http://localhost:3000
echo 📡 后端API地址: http://localhost:8000
echo.
echo ⚠️  按 Ctrl+C 停止服务器
echo.

python app.py

pause 