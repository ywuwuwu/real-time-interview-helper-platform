#!/usr/bin/env python3
"""
测试AI推荐功能
验证基于技能差距分析的个性化推荐生成
"""

import asyncio
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.planner_analysis import PlannerAnalysisService
from config import config

async def test_ai_recommendations():
    """测试AI推荐功能"""
    print("🧪 开始测试AI推荐功能...")
    
    # 初始化服务
    api_key = config.OPENAI_API_KEY
    planner_analysis = PlannerAnalysisService(api_key)
    
    # 模拟分析结果
    analysis_result = {
        "skill_match": 35.0,
        "experience_match": 60.0,
        "overall_match": 47.5,
        "gaps": [
            {
                "skill": "Machine Learning",
                "status": "missing",
                "priority": "high",
                "similar_skill": None
            },
            {
                "skill": "System Design",
                "status": "missing", 
                "priority": "high",
                "similar_skill": None
            },
            {
                "skill": "Python",
                "status": "partial",
                "priority": "medium",
                "similar_skill": "Programming"
            },
            {
                "skill": "Data Processing",
                "status": "missing",
                "priority": "medium",
                "similar_skill": None
            },
            {
                "skill": "A/B Testing",
                "status": "missing",
                "priority": "low",
                "similar_skill": None
            }
        ],
        "strengths": [
            {
                "skill": "Software Development",
                "importance": "high"
            },
            {
                "skill": "Project Management",
                "importance": "medium"
            },
            {
                "skill": "Git",
                "importance": "medium"
            }
        ]
    }
    
    print(f"📊 模拟分析结果:")
    print(f"  - 技能匹配度: {analysis_result['skill_match']}%")
    print(f"  - 经验匹配度: {analysis_result['experience_match']}%")
    print(f"  - 整体匹配度: {analysis_result['overall_match']}%")
    print(f"  - 技能差距: {len(analysis_result['gaps'])} 项")
    print(f"  - 技能优势: {len(analysis_result['strengths'])} 项")
    
    try:
        # 生成AI推荐
        print("\n🎯 开始生成AI推荐...")
        recommendations = await planner_analysis.generate_recommendations(analysis_result)
        
        print(f"\n✅ AI推荐生成成功:")
        print(f"  - 推荐课程: {len(recommendations.get('courses', []))} 项")
        print(f"  - 推荐项目: {len(recommendations.get('projects', []))} 项")
        print(f"  - 推荐练习: {len(recommendations.get('practice', []))} 项")
        
        # 显示课程详情
        if recommendations.get('courses'):
            print(f"\n📚 推荐课程详情:")
            for i, course in enumerate(recommendations['courses'], 1):
                print(f"  {i}. {course.get('name', 'N/A')}")
                print(f"     平台: {course.get('platform', 'N/A')}")
                print(f"     难度: {course.get('difficulty', 'N/A')}")
                print(f"     时长: {course.get('duration', 'N/A')}")
                print(f"     优先级: {course.get('priority', 'N/A')}")
                if course.get('target_skill'):
                    print(f"     目标技能: {course['target_skill']}")
                print(f"     描述: {course.get('description', 'N/A')}")
                print()
        
        # 显示项目详情
        if recommendations.get('projects'):
            print(f"💻 推荐项目详情:")
            for i, project in enumerate(recommendations['projects'], 1):
                print(f"  {i}. {project.get('name', 'N/A')}")
                print(f"     技术栈: {', '.join(project.get('tech_stack', []))}")
                print(f"     难度: {project.get('difficulty', 'N/A')}")
                print(f"     时长: {project.get('duration', 'N/A')}")
                print(f"     描述: {project.get('description', 'N/A')}")
                if project.get('learning_objectives'):
                    print(f"     学习目标: {', '.join(project['learning_objectives'])}")
                if project.get('target_skills'):
                    print(f"     目标技能: {', '.join(project['target_skills'])}")
                print()
        
        # 显示练习详情
        if recommendations.get('practice'):
            print(f"🎤 推荐练习详情:")
            for i, practice in enumerate(recommendations['practice'], 1):
                print(f"  {i}. {practice.get('type', 'N/A')}")
                print(f"     频率: {practice.get('frequency', 'N/A')}")
                print(f"     重点: {practice.get('focus', 'N/A')}")
                print(f"     描述: {practice.get('description', 'N/A')}")
                if practice.get('target_skills'):
                    print(f"     目标技能: {', '.join(practice['target_skills'])}")
                print()
        
        # 显示学习路径
        if recommendations.get('learning_path'):
            learning_path = recommendations['learning_path']
            print(f"🛤️ 学习路径:")
            if learning_path.get('short_term'):
                print(f"  短期目标: {', '.join(learning_path['short_term'])}")
            if learning_path.get('medium_term'):
                print(f"  中期目标: {', '.join(learning_path['medium_term'])}")
            if learning_path.get('long_term'):
                print(f"  长期目标: {', '.join(learning_path['long_term'])}")
            print()
        
        # 显示时间线
        if recommendations.get('timeline'):
            timeline = recommendations['timeline']
            print(f"⏰ 预计时间线:")
            print(f"  预计完成时间: {timeline.get('estimated_weeks', 'N/A')} 周")
            if timeline.get('milestones'):
                print(f"  关键里程碑:")
                for milestone in timeline['milestones']:
                    print(f"    - {milestone}")
            print()
        
        # 保存结果到文件
        output_file = "ai_recommendations_test_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, ensure_ascii=False, indent=2)
        
        print(f"💾 测试结果已保存到: {output_file}")
        
        return recommendations
        
    except Exception as e:
        print(f"❌ AI推荐生成失败: {e}")
        return None

async def test_smart_fallback():
    """测试智能备用推荐"""
    print("\n🧪 测试智能备用推荐...")
    
    api_key = config.OPENAI_API_KEY
    planner_analysis = PlannerAnalysisService(api_key)
    
    # 模拟分析结果
    analysis_result = {
        "skill_match": 20.0,
        "experience_match": 40.0,
        "overall_match": 30.0,
        "gaps": [
            {"skill": "Machine Learning", "priority": "high"},
            {"skill": "Python", "priority": "medium"},
            {"skill": "System Design", "priority": "high"}
        ],
        "strengths": []
    }
    
    try:
        # 测试智能备用推荐
        fallback_recommendations = planner_analysis._generate_smart_fallback_recommendations(analysis_result)
        
        print(f"✅ 智能备用推荐生成成功:")
        print(f"  - 推荐课程: {len(fallback_recommendations.get('courses', []))} 项")
        print(f"  - 推荐项目: {len(fallback_recommendations.get('projects', []))} 项")
        print(f"  - 推荐练习: {len(fallback_recommendations.get('practice', []))} 项")
        
        # 保存备用推荐结果
        output_file = "smart_fallback_test_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fallback_recommendations, f, ensure_ascii=False, indent=2)
        
        print(f"💾 备用推荐结果已保存到: {output_file}")
        
        return fallback_recommendations
        
    except Exception as e:
        print(f"❌ 智能备用推荐失败: {e}")
        return None

async def main():
    """主测试函数"""
    print("🚀 开始AI推荐功能测试...")
    print("=" * 50)
    
    # 测试AI推荐
    ai_result = await test_ai_recommendations()
    
    print("\n" + "=" * 50)
    
    # 测试智能备用推荐
    fallback_result = await test_smart_fallback()
    
    print("\n" + "=" * 50)
    
    if ai_result and fallback_result:
        print("✅ 所有测试通过!")
        print("🎉 AI推荐功能已成功接入!")
    else:
        print("❌ 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    asyncio.run(main()) 