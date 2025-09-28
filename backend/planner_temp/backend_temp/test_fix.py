#!/usr/bin/env python3
"""
测试JSON解析修复
"""

import asyncio
from services.planner_analysis import PlannerAnalysisService
from config import config

async def test_json_fix():
    """测试JSON解析修复"""
    print("🔧 测试JSON解析修复...")
    
    # 初始化服务
    planner_service = PlannerAnalysisService(config.OPENAI_API_KEY)
    
    # 测试简单的技能提取
    simple_jd = "需要Python和React开发经验，熟悉Docker"
    
    try:
        print("📝 测试技能提取...")
        skills = planner_service.extract_skills_from_jd(simple_jd)
        print(f"✅ 提取成功: {len(skills.get('required_skills', []))} 个技能")
        
        # 测试技能差距分析
        user_skills = ["Python", "JavaScript"]
        gaps = planner_service.analyze_skill_gaps(
            skills.get("required_skills", []), 
            user_skills
        )
        print(f"✅ 差距分析成功: {gaps['gap_count']} 个差距, {gaps['strength_count']} 个优势")
        
        # 测试完整分析
        print("🎯 测试完整分析...")
        analysis_result = await planner_service.analyze_job_match(
            simple_jd, user_skills, 2
        )
        
        print(f"✅ 完整分析成功:")
        print(f"  - 技能匹配度: {analysis_result['skill_match']}%")
        print(f"  - 经验匹配度: {analysis_result['experience_match']}%")
        print(f"  - 整体匹配度: {analysis_result['overall_match']}%")
        
        print("\n🎉 JSON解析修复测试成功！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 JSON解析修复测试")
    print("=" * 50)
    
    asyncio.run(test_json_fix())
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！")
    print("=" * 50) 