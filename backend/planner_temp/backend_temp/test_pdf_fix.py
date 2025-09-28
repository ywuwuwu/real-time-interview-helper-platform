#!/usr/bin/env python3
"""
测试PDF解析修复
"""

import asyncio
import json
import os
from services.planner_analysis import PlannerAnalysisService
from config import config

async def test_pdf_fix():
    """测试PDF解析修复"""
    print("🚀 测试PDF解析修复...")
    
    # 创建测试简历内容（模拟PDF内容）
    test_resume_content = """Position: Software Engineer, Machine Learning – Off-Search Sourcing and Relevance
Professional Summary
- 4+ years of full SDLC experience: software development, design, implementation, testing, and operations
- Expert in software development best practices: coding standards, code reviews, and source control management
- Proven ability in system design and architecture for high-concurrency, distributed systems
- Skilled in machine learning: data pipelines, feature engineering, model training, A/B testing, and deployment
- Experienced in DevOps and operations: CI/CD, monitoring, troubleshooting, and production support

Core Skills
- Software Development
- Machine Learning
- Data Pipelines
- Distributed Systems
- System Design
- Programming Languages
- A/B Testing
- Statistics
- Information Retrieval

Professional Experience
Senior Software Engineer | ABC Tech Co., Ltd.
July 2022 – Present, Beijing
- Led end-to-end software development, from architecture design through testing and operations
- Established and enforced coding standards and code review processes, improving code quality by 30%
- Managed Git-based source control workflows with branching strategies and pull request best practices
- Architected a distributed system for low-latency ad serving handling 100M+ QPS with fault tolerance
- Built real-time data pipelines (Kafka → Spark Streaming → HBase) for feature extraction and model inputs
- Developed and deployed ML models in TensorFlow; performed A/B testing to validate improvements
- Oversaw system monitoring and production incident management, ensuring 99.9% uptime

Software Engineer | DEF Information Technology Ltd.
June 2019 – June 2022, Shanghai
- Designed and implemented an offline ETL pipeline processing hundreds of billions of records using Spark and Hadoop
- Automated testing workflows with pytest and Jenkins; reduced manual QA time by 50%
- Participated in system design reviews to improve scalability and reliability
- Collaborated on code reviews and maintained high code quality standards
- Managed production operations and optimized CI/CD pipelines

Selected Projects
Off-Search Ad Relevance Engine
- Role: Lead Architect & Developer
- Tech & Practices: microservices, gRPC, Kafka, TensorFlow, automated testing, Kubernetes
- Impact: 6% uplift in off-search CTR, 8% incremental revenue

Real-Time CTR Prediction Pipeline
- Role: Full-Stack Engineer
- Tech & Practices: real-time streaming, pipeline orchestration, CI/CD, monitoring, A/B testing
- Impact: Maintained <50ms p99 latency with 24/7 stability

Education
Bachelor of Science in Computer Science | Peking University
September 2015 – June 2019

Certifications & Honors
- AWS Certified Solutions Architect – Associate
- TensorFlow Developer Certificate
- Engineer of the Year – ABC Tech Co., Ltd. (2023)

Open Source & Community
- GitHub: https://github.com/your-username
- Contributions: Spark plugins, Feature Store reference implementation"""
    
    # 保存测试简历文件（文本格式，模拟PDF内容）
    test_resume_path = "test_resume_full_skills.txt"
    with open(test_resume_path, 'w', encoding='utf-8') as f:
        f.write(test_resume_content)
    
    try:
        # 初始化服务
        planner_service = PlannerAnalysisService(config.OPENAI_API_KEY)
        
        # 测试简历解析
        print("\n📄 测试简历解析...")
        resume_data = await planner_service.parse_resume(test_resume_path)
        
        print(f"\n✅ 简历解析结果:")
        print(f"  - 技能: {resume_data['skills']}")
        print(f"  - 工作经验: {resume_data['experience_years']} 年")
        print(f"  - 学历: {resume_data['education']}")
        print(f"  - 项目: {resume_data['projects']}")
        print(f"  - 语言: {resume_data['languages']}")
        print(f"  - 认证: {resume_data['certifications']}")
        
        # 测试技能匹配分析
        print("\n🎯 测试技能匹配分析...")
        jd_description = """
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
        """
        
        analysis_result = await planner_service.analyze_job_match(
            jd_description,
            resume_data['skills'],
            resume_data['experience_years']
        )
        
        print(f"\n📊 匹配度分析结果:")
        print(f"  - 技能匹配度: {analysis_result['skill_match']}%")
        print(f"  - 经验匹配度: {analysis_result['experience_match']}%")
        print(f"  - 整体匹配度: {analysis_result['overall_match']}%")
        print(f"  - 差距数量: {len(analysis_result['gaps'])}")
        print(f"  - 优势数量: {len(analysis_result['strengths'])}")
        
        # 显示差距详情
        if analysis_result['gaps']:
            print("\n📋 技能差距详情:")
            for gap in analysis_result['gaps']:
                status_icon = "❌" if gap['status'] == 'missing' else "⚠️"
                print(f"  {status_icon} {gap['skill']} ({gap['priority']} priority)")
        
        # 显示优势详情
        if analysis_result['strengths']:
            print("\n✅ 技能优势详情:")
            for strength in analysis_result['strengths']:
                print(f"  ✅ {strength['skill']} (重要性: {strength['importance']})")
        
        # 详细技能分析
        user_skills = set(skill.lower() for skill in resume_data['skills'])
        matched_skills = set(strength['skill'].lower() for strength in analysis_result.get('strengths', []))
        gap_skills = set(gap['skill'].lower() for gap in analysis_result.get('gaps', []))
        extra_skills = user_skills - matched_skills - gap_skills
        
        print(f"\n🔍 详细技能分析:")
        print(f"  - 用户技能总数: {len(resume_data['skills'])}")
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
        print(f"  - 匹配率: {len(analysis_result.get('strengths', []))}/{len(resume_data['skills'])} = {analysis_result['skill_match']:.1f}%")
        print(f"  - 优势技能: {len(analysis_result.get('strengths', []))} 项")
        print(f"  - 需要提升: {len(analysis_result.get('gaps', []))} 项")
        print(f"  - 额外技能: {len(extra_skills)} 项")
        
        # 保存测试结果
        test_result = {
            "resume_content": test_resume_content,
            "parsed_resume": resume_data,
            "analysis_result": analysis_result,
            "detailed_analysis": {
                "user_skills": list(user_skills),
                "matched_skills": list(matched_skills),
                "gap_skills": list(gap_skills),
                "extra_skills": list(extra_skills),
                "skill_summary": {
                    "total_user_skills": len(resume_data['skills']),
                    "matched_count": len(analysis_result.get('strengths', [])),
                    "missing_count": len(analysis_result.get('gaps', [])),
                    "extra_count": len(extra_skills),
                    "match_rate": analysis_result['skill_match']
                }
            }
        }
        
        with open('pdf_fix_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(test_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 测试结果已保存到 pdf_fix_test_result.json")
        print("\n🎉 PDF解析修复测试成功！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        if os.path.exists(test_resume_path):
            os.remove(test_resume_path)

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PDF解析修复测试")
    print("=" * 60)
    
    asyncio.run(test_pdf_fix())
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60) 