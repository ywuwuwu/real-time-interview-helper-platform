#!/usr/bin/env python3
"""
简化版增强Planner AI功能测试
"""

import asyncio
import json
from services.planner_analysis import PlannerAnalysisService
from config import config

async def test_simple_enhanced_planner():
    """测试简化版增强的Planner功能"""
    print("🚀 开始测试简化版增强的Planner AI功能...")
    
    # 初始化服务
    planner_service = PlannerAnalysisService(config.OPENAI_API_KEY)
    
    # 测试数据
    job_description = """
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
    """
    
    user_skills = ["Python", "JavaScript", "React", "Git", "MySQL", "Docker"]
    experience_years = 2
    
    print(f"\n📝 职位描述: {job_description[:100]}...")
    print(f"👤 用户技能: {', '.join(user_skills)}")
    print(f"⏰ 工作经验: {experience_years}年")
    
    try:
        # 测试技能提取
        print("\n🔍 测试技能提取...")
        jd_skills = planner_service.extract_skills_from_jd(job_description)
        print(f"✅ 提取到 {len(jd_skills.get('required_skills', []))} 个必需技能")
        print(f"📋 技能列表: {[skill['skill'] for skill in jd_skills.get('required_skills', [])]}")
        
        # 测试技能差距分析
        print("\n📊 测试技能差距分析...")
        skill_gaps = planner_service.analyze_skill_gaps(
            jd_skills.get("required_skills", []), 
            user_skills
        )
        print(f"✅ 差距数量: {skill_gaps['gap_count']}")
        print(f"✅ 优势数量: {skill_gaps['strength_count']}")
        
        # 显示差距详情
        print("\n📋 技能差距详情:")
        for gap in skill_gaps['gaps'][:3]:  # 显示前3个差距
            print(f"  - {gap['skill']} ({gap['status']}, 优先级: {gap['priority']})")
        
        # 显示优势详情
        print("\n✅ 技能优势详情:")
        for strength in skill_gaps['strengths'][:3]:  # 显示前3个优势
            print(f"  - {strength['skill']} (重要性: {strength['importance']})")
        
        # 测试完整的职位匹配分析
        print("\n🎯 测试完整的职位匹配分析...")
        analysis_result = await planner_service.analyze_job_match(
            job_description, user_skills, experience_years
        )
        
        print(f"✅ 技能匹配度: {analysis_result['skill_match']}%")
        print(f"✅ 经验匹配度: {analysis_result['experience_match']}%")
        print(f"✅ 整体匹配度: {analysis_result['overall_match']}%")
        print(f"✅ 置信度分数: {analysis_result['confidence_score']}%")
        
        # 显示详细分析
        print("\n📋 详细分析结果:")
        detailed = analysis_result.get('detailed_analysis', {})
        print(f"  核心竞争力: {', '.join(detailed.get('core_competencies', []))}")
        print(f"  主要差距: {', '.join(detailed.get('main_gaps', []))}")
        print(f"  短期目标: {', '.join(detailed.get('short_term_goals', []))}")
        
        # 显示改进优先级
        print("\n🎯 改进优先级:")
        priorities = analysis_result.get('improvement_priorities', [])
        for i, priority in enumerate(priorities[:3], 1):
            print(f"  {i}. {priority['skill']} (优先级: {priority['priority_score']}, 预计时间: {priority['estimated_time']})")
        
        # 显示时间线估算
        print("\n⏰ 改进时间线:")
        timeline = analysis_result.get('timeline_estimate', {})
        print(f"  总周数: {timeline.get('total_weeks', 0)}周")
        print(f"  预计完成日期: {timeline.get('estimated_completion_date', 'N/A')}")
        
        # 保存详细结果到文件
        with open('simple_enhanced_planner_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 详细结果已保存到 simple_enhanced_planner_test_result.json")
        
        print("\n🎉 简化版增强的Planner AI功能测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_basic_functionality():
    """测试基本功能"""
    print("\n🔧 测试基本功能...")
    
    planner_service = PlannerAnalysisService(config.OPENAI_API_KEY)
    
    # 测试简单的技能提取
    simple_jd = "需要Python和React开发经验"
    skills = planner_service.extract_skills_from_jd(simple_jd)
    print(f"✅ 简单JD技能提取: {[skill['skill'] for skill in skills.get('required_skills', [])]}")
    
    # 测试技能差距分析
    user_skills = ["Python", "JavaScript"]
    gaps = planner_service.analyze_skill_gaps(
        skills.get("required_skills", []), 
        user_skills
    )
    print(f"✅ 技能差距分析: {gaps['gap_count']} 个差距, {gaps['strength_count']} 个优势")
    
    print("\n✅ 基本功能测试完成！")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 简化版增强的Planner AI功能测试")
    print("=" * 60)
    
    # 运行测试
    asyncio.run(test_simple_enhanced_planner())
    asyncio.run(test_basic_functionality())
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60) 