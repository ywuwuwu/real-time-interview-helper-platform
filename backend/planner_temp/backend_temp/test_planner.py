#!/usr/bin/env python3
"""
测试Interview Planner API功能
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_create_plan():
    """测试创建面试计划"""
    print("🔍 测试创建面试计划...")
    
    plan_data = {
        "job_title": "Software Engineer",
        "job_description": "We are looking for a software engineer with experience in Python, React, and cloud technologies. The ideal candidate should have 3+ years of experience in web development and be familiar with Docker and Kubernetes.",
        "target_company": "Tech Corp",
        "experience_years": 3,
        "skills": ["Python", "React", "JavaScript", "Git"],
        "career_goals": "成为全栈开发工程师，掌握云原生技术"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/planner/create",
        json=plan_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 创建成功！计划ID: {result['id']}")
        print(f"职位: {result['job_title']}")
        print(f"技能匹配度: {result['skill_match_score']}")
        print(f"经验匹配度: {result['experience_match_score']}")
        print(f"推荐课程数量: {len(result['recommended_courses'])}")
        print(f"推荐项目数量: {len(result['recommended_projects'])}")
        print(f"推荐练习数量: {len(result['recommended_practice'])}")
        return result['id']
    else:
        print(f"❌ 创建失败: {response.text}")
        return None
    print()

def test_get_plan(plan_id):
    """测试获取面试计划"""
    print(f"🔍 测试获取面试计划 {plan_id}...")
    
    response = requests.get(f"{BASE_URL}/api/planner/{plan_id}")
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 获取成功！")
        print(f"职位: {result['job_title']}")
        print(f"进度: {result['progress']}")
    else:
        print(f"❌ 获取失败: {response.text}")
    print()

def test_update_progress(plan_id):
    """测试更新进度"""
    print(f"🔍 测试更新进度 {plan_id}...")
    
    progress_data = {
        "activity_type": "course",
        "activity_id": "course_1",
        "activity_name": "Docker容器化实践",
        "progress_percentage": 75.0,
        "completed": False
    }
    
    response = requests.post(
        f"{BASE_URL}/api/planner/{plan_id}/progress",
        json=progress_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 更新成功！")
        print(f"进度: {result['progress']}")
    else:
        print(f"❌ 更新失败: {response.text}")
    print()

def main():
    """主测试函数"""
    print("🚀 开始测试Interview Planner API...")
    print("=" * 50)
    
    # 测试健康检查
    test_health()
    
    # 测试创建计划
    plan_id = test_create_plan()
    
    if plan_id:
        # 测试获取计划
        test_get_plan(plan_id)
        
        # 测试更新进度
        test_update_progress(plan_id)
        
        # 再次获取计划查看进度变化
        test_get_plan(plan_id)
    
    print("✅ 测试完成！")

if __name__ == "__main__":
    main() 