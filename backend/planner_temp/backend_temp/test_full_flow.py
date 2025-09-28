#!/usr/bin/env python3
"""
完整流程测试 - 模拟前端到后端的完整交互
"""

import asyncio
import json
import requests
from services.planner_analysis import PlannerAnalysisService
from config import config

async def test_full_flow():
    """测试完整流程"""
    print("🚀 测试完整流程...")
    
    # 模拟前端请求数据
    plan_request = {
        "job_title": "全栈开发工程师",
        "job_description": """
        我们正在寻找一位经验丰富的全栈开发工程师，负责开发和维护我们的Web应用程序。
        
        职位要求：
        - 3年以上Python开发经验
        - 熟练掌握React.js和现代前端技术
        - 有Docker和AWS使用经验
        - 熟悉数据库设计和管理（MySQL/PostgreSQL）
        - 具备良好的团队协作和沟通能力
        - 有微服务架构经验优先
        
        职责：
        - 设计和开发新的功能模块
        - 优化现有系统性能
        - 参与代码审查和技术讨论
        - 与产品团队协作，理解需求并实现
        """,
        "target_company": "科技公司",
        "experience_years": 2,
        "skills": ["Python", "JavaScript", "React", "Git", "MySQL", "Docker"],
        "career_goals": "成为技术专家"
    }
    
    try:
        # 1. 测试直接调用PlannerAnalysisService
        print("\n📝 测试PlannerAnalysisService...")
        planner_service = PlannerAnalysisService(config.OPENAI_API_KEY)
        
        analysis_result = await planner_service.analyze_job_match(
            plan_request["job_description"],
            plan_request["skills"],
            plan_request["experience_years"]
        )
        
        print(f"✅ 分析成功:")
        print(f"  - 技能匹配度: {analysis_result['skill_match']}%")
        print(f"  - 经验匹配度: {analysis_result['experience_match']}%")
        print(f"  - 整体匹配度: {analysis_result['overall_match']}%")
        print(f"  - 差距数量: {len(analysis_result['gaps'])}")
        print(f"  - 优势数量: {len(analysis_result['strengths'])}")
        
        # 2. 测试推荐生成
        print("\n💡 测试推荐生成...")
        recommendations = await planner_service.generate_recommendations(analysis_result)
        
        print(f"✅ 推荐生成成功:")
        print(f"  - 课程数量: {len(recommendations.get('courses', []))}")
        print(f"  - 项目数量: {len(recommendations.get('projects', []))}")
        print(f"  - 练习数量: {len(recommendations.get('practice', []))}")
        
        # 3. 测试API端点（如果服务器运行）
        print("\n🌐 测试API端点...")
        try:
            response = requests.post(
                "http://localhost:8000/api/planner/create",
                json=plan_request,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API调用成功:")
                print(f"  - Plan ID: {result.get('id')}")
                print(f"  - 技能匹配度: {result.get('skill_match_score')}%")
                print(f"  - 经验匹配度: {result.get('experience_match_score')}%")
            else:
                print(f"⚠️ API调用失败: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            print("⚠️ 服务器未运行，跳过API测试")
        except Exception as e:
            print(f"⚠️ API测试失败: {e}")
        
        # 4. 保存完整结果
        full_result = {
            "request": plan_request,
            "analysis": analysis_result,
            "recommendations": recommendations
        }
        
        with open('full_flow_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(full_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 完整结果已保存到 full_flow_test_result.json")
        print("\n🎉 完整流程测试成功！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 完整流程测试")
    print("=" * 60)
    
    asyncio.run(test_full_flow())
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60) 