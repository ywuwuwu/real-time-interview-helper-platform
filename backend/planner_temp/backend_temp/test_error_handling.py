#!/usr/bin/env python3
"""
测试简历解析错误处理功能
"""

import asyncio
import json
import os
from services.planner_analysis import PlannerAnalysisService
from config import config

async def test_error_handling():
    """测试错误处理功能"""
    print("🚀 测试简历解析错误处理...")
    
    # 初始化服务
    planner_service = PlannerAnalysisService(config.OPENAI_API_KEY)
    
    # 测试1: 不存在的文件
    print("\n📄 测试1: 不存在的文件")
    try:
        result = await planner_service.parse_resume("nonexistent_file.pdf")
        print("❌ 应该抛出错误但没有")
    except ValueError as e:
        print(f"✅ 正确抛出错误: {e}")
    
    # 测试2: 空文件
    print("\n📄 测试2: 空文件")
    empty_file = "test_empty.txt"
    with open(empty_file, 'w') as f:
        f.write("")
    
    try:
        result = await planner_service.parse_resume(empty_file)
        print("❌ 应该抛出错误但没有")
    except ValueError as e:
        print(f"✅ 正确抛出错误: {e}")
    
    # 清理
    if os.path.exists(empty_file):
        os.remove(empty_file)
    
    # 测试3: 内容过短的文件
    print("\n📄 测试3: 内容过短的文件")
    short_file = "test_short.txt"
    with open(short_file, 'w') as f:
        f.write("Hello")
    
    try:
        result = await planner_service.parse_resume(short_file)
        print("❌ 应该抛出错误但没有")
    except ValueError as e:
        print(f"✅ 正确抛出错误: {e}")
    
    # 清理
    if os.path.exists(short_file):
        os.remove(short_file)
    
    # 测试4: 正常文件（应该成功）
    print("\n📄 测试4: 正常文件")
    normal_file = "test_normal.txt"
    normal_content = """Position: Software Engineer
Professional Summary
- 4+ years of software development experience
- Expert in Python, Java, and machine learning
- Skilled in distributed systems and data processing

Core Skills
- Python, Java, Scala
- Machine Learning, TensorFlow
- Distributed Systems, Docker, Kubernetes
- Data Processing, Spark, Kafka

Experience
Senior Software Engineer | ABC Tech Co., Ltd.
July 2022 – Present
- Led end-to-end software development
- Built real-time data processing pipelines
- Developed ML models in TensorFlow

Education
Bachelor of Science in Computer Science | Peking University"""
    
    with open(normal_file, 'w', encoding='utf-8') as f:
        f.write(normal_content)
    
    try:
        result = await planner_service.parse_resume(normal_file)
        print(f"✅ 正常文件解析成功:")
        print(f"  - 技能: {result['skills']}")
        print(f"  - 经验: {result['experience_years']} 年")
        print(f"  - 学历: {result['education']}")
    except Exception as e:
        print(f"❌ 正常文件解析失败: {e}")
    
    # 清理
    if os.path.exists(normal_file):
        os.remove(normal_file)
    
    print("\n🎉 错误处理测试完成！")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 简历解析错误处理测试")
    print("=" * 60)
    
    asyncio.run(test_error_handling())
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60) 