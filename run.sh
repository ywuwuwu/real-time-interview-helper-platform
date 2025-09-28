#!/bin/bash

# 进入项目根目录下的 interview-helper
cd "$(dirname "$0")"

echo "------ 启动 FastAPI 后端 (端口8000) ------"
cd backend
# 使用nohup后台运行，输出日志到backend.log
nohup uvicorn app:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "后端进程PID: $BACKEND_PID"

cd ../frontend
echo "------ 启动前端 Vite (端口5173) ------"
# 同样后台运行，输出日志到frontend.log
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端进程PID: $FRONTEND_PID"

cd ..

echo "✅ 后端已启动: http://localhost:8000"
echo "✅ 前端已启动: http://localhost:5173"
echo "日志见 backend.log 和 frontend.log"
echo "如需关闭服务，可用 kill $BACKEND_PID $FRONTEND_PID"

# pkill -f uvicorn
# pkill -f npm
