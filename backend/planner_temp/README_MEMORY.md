# Interview Helper - 基于内存存储版本

## 概述

这是一个不使用数据库的简化版本，使用内存存储来实现Interview Planner功能。所有数据存储在内存中，重启后数据会丢失。

## 文件结构

```
backend/
├── app_memory.py          # 基于内存的主应用文件
├── run_memory.py          # 启动脚本
├── test_planner.py        # API测试脚本
└── README_MEMORY.md       # 本说明文档
```

## 启动服务

### 方法1：直接运行
```bash
cd backend
python app_memory.py
```

### 方法2：使用启动脚本
```bash
cd backend
python run_memory.py
```

## 测试API

运行测试脚本来验证功能：
```bash
cd backend
python test_planner.py
```

## API端点

### 健康检查
- **GET** `/api/health`
- 返回服务状态

### Interview Planner
- **POST** `/api/planner/create` - 创建面试计划
- **GET** `/api/planner/{plan_id}` - 获取计划详情
- **POST** `/api/planner/{plan_id}/progress` - 更新进度
- **POST** `/api/planner/{plan_id}/upload-resume` - 上传简历
- **GET** `/api/planner/user/{user_id}/summary` - 获取用户总结

### 其他功能
- **POST** `/api/rag` - RAG问答
- **POST** `/api/tts` - 文本转语音
- **POST** `/api/rag-tts` - RAG+TTS组合

## 功能特点

### ✅ 已实现
- 面试计划创建和管理
- 技能匹配分析
- 个性化推荐（课程、项目、练习）
- 进度跟踪
- 简历上传和解析
- 内存存储（无需数据库）

### 🔄 模拟数据
- AI分析结果使用模拟数据
- 推荐内容为预设数据
- 简历解析返回模拟结果

## 前端集成

前端代码无需修改，可以直接使用现有的API调用。确保前端指向正确的后端地址：

```javascript
// 在 frontend/src/api.js 中
const BASE_URL = "http://localhost:8000";
```

## 优势

1. **无需数据库** - 不需要SQLite或其他数据库
2. **快速启动** - 无需初始化数据库表
3. **简单部署** - 只需要Python环境
4. **易于测试** - 可以快速验证功能

## 限制

1. **数据持久化** - 重启后数据丢失
2. **并发限制** - 内存存储不适合多用户
3. **功能简化** - 部分高级功能使用模拟数据

## 故障排除

### 服务无法启动
1. 检查端口8000是否被占用
2. 确保所有依赖已安装
3. 检查Python版本（建议3.8+）

### API返回404
1. 确保运行的是`app_memory.py`而不是`app.py`
2. 检查服务是否正常启动
3. 验证API端点路径

### 测试失败
1. 确保服务正在运行
2. 检查网络连接
3. 查看服务日志

## 下一步

如果需要持久化存储，可以考虑：
1. 使用JSON文件存储
2. 集成轻量级数据库（如SQLite）
3. 使用Redis等内存数据库 