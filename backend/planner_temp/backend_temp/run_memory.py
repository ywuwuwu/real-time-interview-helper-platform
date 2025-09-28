#!/usr/bin/env python3
"""
启动基于内存存储的Interview Helper后端服务
"""

import uvicorn
from app_memory import app

if __name__ == "__main__":
    print("🚀 启动基于内存存储的Interview Helper后端服务...")
    print("📝 注意：此版本使用内存存储，重启后数据会丢失")
    print("🌐 服务地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 