#!/usr/bin/env python3
"""
测试详细技能分析功能
"""

import asyncio
import json
import requests
from services.planner_analysis import PlannerAnalysisService
from config import config

async def test_detailed_analysis():
    """测试详细技能分析功能"""
    print("🚀 测试详细技能分析功能...")
    
    # 模拟前端请求数据
    plan_request = {
        "job_title": "数据科学家",
        "job_description": """
        我们正在寻找一位经验丰富的数据科学家，负责开发和维护我们的机器学习系统。
        
        职位要求：
        - 3年以上Python开发经验
        - 熟练掌握机器学习算法和统计方法
        - 有分布式系统和大数据处理经验
        - 熟悉A/B测试和实验设计
        - 具备良好的编程规范和设计模式
        - 有自然语言处理经验优先
        
        职责：
        - 设计和开发机器学习模型
        - 进行数据分析和统计建模
        - 参与代码审查和技术讨论
        - 与产品团队协作，理解需求并实现
        """,
        "target_company": "科技公司",
        "experience_years": 4,
        "skills": ["Python", "TensorFlow", "PyTorch", "scikit-learn", "Apache Spark", "Kafka", "Hadoop", "Docker", "Kubernetes", "AWS", "React", "Node.js", "MongoDB"],
        "career_goals": "成为机器学习专家"
    }
    
    try:
        # 1. 测试创建计划
        print("\n📝 测试创建计划...")
        response = requests.post(
            "http://localhost:8000/api/planner/create",
            json=plan_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            plan_id = result.get('id')
            print(f"✅ 计划创建成功: {plan_id}")
            
            # 2. 测试获取计划详情
            print("\n📋 测试获取计划详情...")
            get_response = requests.get(
                f"http://localhost:8000/api/planner/{plan_id}",
                timeout=30
            )
            
            if get_response.status_code == 200:
                plan_details = get_response.json()
                print(f"✅ 获取计划详情成功")
                
                # 3. 直接测试技能分析
                print("\n🔍 测试详细技能分析...")
                planner_service = PlannerAnalysisService(config.OPENAI_API_KEY)
                
                analysis_result = await planner_service.analyze_job_match(
                    plan_request["job_description"],
                    plan_request["skills"],
                    plan_request["experience_years"]
                )
                
                print(f"\n📊 分析结果:")
                print(f"  - 技能匹配度: {analysis_result['skill_match']}%")
                print(f"  - 经验匹配度: {analysis_result['experience_match']}%")
                print(f"  - 整体匹配度: {analysis_result['overall_match']}%")
                
                # 详细技能分析
                user_skills = set(skill.lower() for skill in plan_request["skills"])
                matched_skills = set(strength['skill'].lower() for strength in analysis_result.get('strengths', []))
                gap_skills = set(gap['skill'].lower() for gap in analysis_result.get('gaps', []))
                extra_skills = user_skills - matched_skills - gap_skills
                
                print(f"\n🔍 详细技能分析:")
                print(f"  - 用户技能总数: {len(plan_request['skills'])}")
                print(f"  - 匹配技能: {len(analysis_result.get('strengths', []))} 项")
                print(f"  - 缺失技能: {len(analysis_result.get('gaps', []))} 项")
                print(f"  - 额外技能: {len(extra_skills)} 项")
                
                # 显示匹配的技能
                if analysis_result.get('strengths'):
                    print(f"\n✅ 匹配的技能:")
                    for strength in analysis_result['strengths']:
                        print(f"    - {strength['skill']} (重要性: {strength['importance']})")
                
                # 显示缺失的技能
                if analysis_result.get('gaps'):
                    print(f"\n❌ 缺失的技能:")
                    for gap in analysis_result['gaps']:
                        status_icon = "❌" if gap['status'] == 'missing' else "⚠️"
                        print(f"    {status_icon} {gap['skill']} ({gap['priority']} priority)")
                        if gap.get('similar_skill'):
                            print(f"      相关技能: {gap['similar_skill']}")
                
                # 显示岗位没有要求的技能
                if extra_skills:
                    print(f"\n💡 岗位没有要求的技能:")
                    for skill in extra_skills:
                        print(f"    - {skill}")
                
                print(f"\n📋 技能匹配总结:")
                print(f"  - 匹配率: {len(analysis_result.get('strengths', []))}/{len(plan_request['skills'])} = {analysis_result['skill_match']:.1f}%")
                print(f"  - 优势技能: {len(analysis_result.get('strengths', []))} 项")
                print(f"  - 需要提升: {len(analysis_result.get('gaps', []))} 项")
                print(f"  - 额外技能: {len(extra_skills)} 项")
                
                # 保存测试结果
                test_result = {
                    "plan_request": plan_request,
                    "analysis_result": analysis_result,
                    "detailed_analysis": {
                        "user_skills": list(user_skills),
                        "matched_skills": list(matched_skills),
                        "gap_skills": list(gap_skills),
                        "extra_skills": list(extra_skills),
                        "skill_summary": {
                            "total_user_skills": len(plan_request['skills']),
                            "matched_count": len(analysis_result.get('strengths', [])),
                            "missing_count": len(analysis_result.get('gaps', [])),
                            "extra_count": len(extra_skills),
                            "match_rate": analysis_result['skill_match']
                        }
                    }
                }
                
                with open('detailed_analysis_test_result.json', 'w', encoding='utf-8') as f:
                    json.dump(test_result, f, ensure_ascii=False, indent=2)
                
                print(f"\n💾 测试结果已保存到 detailed_analysis_test_result.json")
                print("\n🎉 详细技能分析测试成功！")
                
            else:
                print(f"❌ 获取计划详情失败: {get_response.status_code} - {get_response.text}")
                
        else:
            print(f"❌ 计划创建失败: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ 服务器未运行，请先启动后端服务器")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 详细技能分析功能测试")
    print("=" * 60)
    
    asyncio.run(test_detailed_analysis())
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60) 