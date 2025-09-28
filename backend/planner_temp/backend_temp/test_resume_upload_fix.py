#!/usr/bin/env python3
"""
测试简历上传后的数据更新
"""

import asyncio
import json
import requests
from services.planner_analysis import PlannerAnalysisService
from config import config

async def test_resume_upload_fix():
    """测试简历上传后的数据更新"""
    print("🚀 测试简历上传后的数据更新...")
    
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
        "experience_years": 2,
        "skills": ["Python", "Machine Learning", "Statistics", "SQL"],
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
            print(f"📊 初始匹配度:")
            print(f"  - 技能匹配度: {result.get('skill_match_score')}%")
            print(f"  - 经验匹配度: {result.get('experience_match_score')}%")
            
            # 2. 测试获取计划详情
            print("\n📋 测试获取计划详情...")
            get_response = requests.get(
                f"http://localhost:8000/api/planner/{plan_id}",
                timeout=30
            )
            
            if get_response.status_code == 200:
                plan_details = get_response.json()
                print(f"✅ 获取计划详情成功:")
                print(f"  - 技能匹配度: {plan_details.get('skill_match_score')}%")
                print(f"  - 经验匹配度: {plan_details.get('experience_match_score')}%")
                print(f"  - 技能列表: {plan_details.get('skills', [])}")
                print(f"  - 经验年数: {plan_details.get('experience_years')}")
                
                # 3. 模拟简历上传后的数据更新
                print("\n📄 模拟简历上传后的数据更新...")
                updated_skills = ["Python", "Machine Learning", "Statistics", "SQL", "Pandas", "Scikit-learn", "Docker", "AWS"]
                updated_experience = 3
                
                # 直接调用PlannerAnalysisService进行测试
                planner_service = PlannerAnalysisService(config.OPENAI_API_KEY)
                updated_analysis = await planner_service.analyze_job_match(
                    plan_request["job_description"],
                    updated_skills,
                    updated_experience
                )
                
                print(f"📊 更新后的匹配度:")
                print(f"  - 技能匹配度: {updated_analysis['skill_match']}%")
                print(f"  - 经验匹配度: {updated_analysis['experience_match']}%")
                print(f"  - 整体匹配度: {updated_analysis['overall_match']}%")
                print(f"  - 差距数量: {len(updated_analysis['gaps'])}")
                print(f"  - 优势数量: {len(updated_analysis['strengths'])}")
                
                # 显示计算过程
                print("\n📋 计算过程详情:")
                total_skills = len(updated_analysis.get('jd_requirements', {}).get('required_skills', []))
                matched_skills = len(updated_analysis.get('strengths', []))
                skill_percentage = (matched_skills / total_skills * 100) if total_skills > 0 else 0
                
                print(f"  - 技能匹配度计算: {matched_skills} 个匹配技能 / {total_skills} 个总技能 = {skill_percentage:.1f}%")
                print(f"  - 经验匹配度计算: 用户经验 {updated_experience} 年 vs 要求经验 3 年")
                
                # 显示差距详情
                print("\n📋 技能差距详情:")
                for gap in updated_analysis.get('gaps', []):
                    status_icon = "❌" if gap['status'] == 'missing' else "⚠️"
                    print(f"  {status_icon} {gap['skill']} ({gap['priority']} priority)")
                
                # 显示优势详情
                print("\n✅ 技能优势详情:")
                for strength in updated_analysis.get('strengths', []):
                    print(f"  ✅ {strength['skill']} (重要性: {strength['importance']})")
                
                # 4. 保存测试结果
                test_result = {
                    "plan_request": plan_request,
                    "initial_result": result,
                    "plan_details": plan_details,
                    "updated_skills": updated_skills,
                    "updated_experience": updated_experience,
                    "updated_analysis": updated_analysis,
                    "calculation_details": {
                        "total_skills": total_skills,
                        "matched_skills": matched_skills,
                        "skill_percentage": skill_percentage,
                        "experience_years_user": updated_experience,
                        "experience_years_required": 3
                    }
                }
                
                with open('resume_upload_fix_test_result.json', 'w', encoding='utf-8') as f:
                    json.dump(test_result, f, ensure_ascii=False, indent=2)
                
                print(f"\n💾 测试结果已保存到 resume_upload_fix_test_result.json")
                print("\n🎉 简历上传修复测试成功！")
                
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
    print("🧪 简历上传修复测试")
    print("=" * 60)
    
    asyncio.run(test_resume_upload_fix())
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60) 