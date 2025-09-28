#!/usr/bin/env python3
"""
测试真实AI集成功能
"""

import asyncio
import os
from services.real_ai_service import RealAIService
from config import config

async def test_jd_analysis():
    """测试JD解析功能"""
    print("🔍 测试JD解析功能...")
    
    ai_service = RealAIService(config.OPENAI_API_KEY)
    
    jd_text = """
    我们正在寻找一位经验丰富的软件工程师加入我们的团队。
    
    职位要求：
    - 3年以上Python开发经验
    - 熟悉React、JavaScript前端开发
    - 了解Docker、Kubernetes容器化技术
    - 有微服务架构设计经验
    - 良好的团队合作能力
    
    工作职责：
    - 设计和开发新的软件功能
    - 参与代码审查和技术讨论
    - 与产品团队协作，理解业务需求
    - 优化系统性能和用户体验
    
    加分项：
    - AWS云服务经验
    - 机器学习相关经验
    - 开源项目贡献经验
    """
    
    try:
        result = await ai_service.analyze_job_description(jd_text)
        print("✅ JD解析成功！")
        print(f"职位标题: {result.get('job_title')}")
        print(f"必需技能: {result.get('required_skills')}")
        print(f"优先技能: {result.get('preferred_skills')}")
        print(f"经验要求: {result.get('experience_level')}")
        return True
    except Exception as e:
        print(f"❌ JD解析失败: {e}")
        return False

async def test_job_match():
    """测试职位匹配分析"""
    print("\n🔍 测试职位匹配分析...")
    
    ai_service = RealAIService(config.OPENAI_API_KEY)
    
    job_description = "我们寻找有Python和React经验的软件工程师，需要3年以上经验，熟悉Docker和微服务架构。"
    user_skills = ["Python", "JavaScript", "Git", "MySQL"]
    experience_years = 2
    
    try:
        result = await ai_service.analyze_job_match(job_description, user_skills, experience_years)
        print("✅ 职位匹配分析成功！")
        print(f"技能匹配度: {result.get('skill_match')}")
        print(f"经验匹配度: {result.get('experience_match')}")
        print(f"缺失技能: {result.get('gap_analysis', {}).get('missing_skills')}")
        return True
    except Exception as e:
        print(f"❌ 职位匹配分析失败: {e}")
        return False

async def test_recommendations():
    """测试个性化推荐"""
    print("\n🔍 测试个性化推荐...")
    
    ai_service = RealAIService(config.OPENAI_API_KEY)
    
    analysis_result = {
        "skill_match": 0.7,
        "experience_match": 0.6,
        "gap_analysis": {
            "missing_skills": ["Docker", "Kubernetes", "AWS"],
            "skill_gaps": [
                {"skill": "Docker", "importance": "high", "gap_level": "medium"},
                {"skill": "Kubernetes", "importance": "medium", "gap_level": "high"}
            ]
        }
    }
    
    try:
        result = await ai_service.generate_recommendations(analysis_result)
        print("✅ 个性化推荐生成成功！")
        print(f"推荐课程数量: {len(result.get('courses', []))}")
        print(f"推荐项目数量: {len(result.get('projects', []))}")
        print(f"推荐练习数量: {len(result.get('practice', []))}")
        
        if result.get('courses'):
            print(f"第一个推荐课程: {result['courses'][0].get('title')}")
        
        return True
    except Exception as e:
        print(f"❌ 个性化推荐失败: {e}")
        return False

async def test_resume_parsing():
    """测试简历解析"""
    print("\n🔍 测试简历解析...")
    
    ai_service = RealAIService(config.OPENAI_API_KEY)
    
    # 创建一个示例简历文件
    resume_content = """
    张三
    软件工程师
    
    技能：
    - Python, JavaScript, React
    - Git, Docker, MySQL
    - 项目管理，团队协作
    
    工作经验：
    2021-2023 科技公司 软件工程师
    - 开发了电商平台后端API
    - 优化了系统性能，提升30%
    - 领导了3人开发团队
    
    教育背景：
    计算机科学学士学位
    
    项目经验：
    - 电商平台：使用React + Node.js + MongoDB
    - 数据可视化：Python + D3.js + Pandas
    """
    
    # 保存到临时文件
    temp_file = "temp_resume.txt"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(resume_content)
    
    try:
        result = await ai_service.parse_resume(temp_file)
        print("✅ 简历解析成功！")
        print(f"提取技能: {result.get('skills')}")
        print(f"工作经验: {result.get('experience_years')}年")
        print(f"教育背景: {result.get('education')}")
        print(f"项目数量: {len(result.get('projects', []))}")
        
        # 清理临时文件
        os.remove(temp_file)
        return True
    except Exception as e:
        print(f"❌ 简历解析失败: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False

async def main():
    """主测试函数"""
    print("🚀 开始测试真实AI集成功能...")
    print("=" * 50)
    
    # 检查API Key
    if not config.OPENAI_API_KEY:
        print("❌ 未找到OPENAI_API_KEY，请在.env文件中配置")
        return
    
    print(f"✅ 使用模型: {config.LLM_MODEL}")
    
    # 运行所有测试
    tests = [
        test_jd_analysis(),
        test_job_match(),
        test_recommendations(),
        test_resume_parsing()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    passed = 0
    for i, result in enumerate(results):
        test_names = ["JD解析", "职位匹配", "个性化推荐", "简历解析"]
        if result is True:
            print(f"✅ {test_names[i]}: 通过")
            passed += 1
        else:
            print(f"❌ {test_names[i]}: 失败")
    
    print(f"\n🎯 总体结果: {passed}/{len(tests)} 个测试通过")
    
    if passed == len(tests):
        print("🎉 所有AI功能测试通过！真实AI集成成功！")
    else:
        print("⚠️  部分功能需要检查，请查看错误信息")

if __name__ == "__main__":
    asyncio.run(main()) 