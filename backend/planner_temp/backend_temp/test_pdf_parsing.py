#!/usr/bin/env python3
"""
测试PDF解析功能
"""

import asyncio
import json
import os
from services.planner_analysis import PlannerAnalysisService
from config import config

async def test_pdf_parsing():
    """测试PDF解析功能"""
    print("🚀 测试PDF解析功能...")
    
    # 创建测试简历内容
    test_resume_content = """Name: XXX
Position: Software Engineer, Machine Learning – Off-Search Sourcing and Relevance
Professional Summary
- 4+ years of full-lifecycle software development experience, from requirements gathering through deployment
- Expert in system design and architecture patterns for high-concurrency, low-latency distributed systems
- Proficient in machine learning model development: data preprocessing, feature engineering, model training
- Skilled at rapid iteration and Agile delivery, delivering incremental value through continuous integration & deployment
- Deep experience with data processing pipelines using Spark, Kafka and Hadoop ecosystems
- Strong command of Python, Java, Scala and SQL for both back-end services and ETL jobs

Core Skills
- Software Development & Architecture: SDLC, design patterns, reliability, scaling, microservices
- High-Concurrency Systems: gRPC, REST, asynchronous processing, load balancing, back-pressure handling
- Machine Learning & Data Science: TensorFlow, PyTorch, scikit-learn, MLflow, online/offline serving
- Data Processing: Apache Spark, Kafka, Hadoop, real-time streaming, batch ETL
- Programming Languages: Python, Java, Scala, SQL
- Cloud & DevOps: AWS (EC2, S3, EMR), Docker, Kubernetes, Terraform, CI/CD (Jenkins/GitHub Actions)
- Agile & Rapid Iteration: Scrum/Kanban, TDD, code review, CI/CD pipelines

Professional Experience
Senior Software Engineer | ABC Tech Co., Ltd.
July 2022 – Present, Beijing
- Architected and designed a high-concurrency, low-latency online ad serving platform handling 100M+ QPS
- Led full software development lifecycle: requirement analysis, API design, coding standards, code reviews
- Built real-time data processing pipelines (Kafka → Spark Streaming → HBase) to compute and serve features
- Developed and deployed TensorFlow-based CTR prediction models; improved prediction accuracy by 7%
- Drove rapid iteration in collaboration with product and data science teams, executing A/B tests

Software Engineer | DEF Information Technology Ltd.
June 2019 – June 2022, Shanghai
- Designed and implemented an offline feature computation platform processing hundreds of billions of records
- Delivered scalable ETL jobs in Python/Java with 200+ parallel tasks, cutting job runtime by 60%
- Contributed to system design for ad ranking and filtering services, improving relevance through iterative algorithms
- Maintained microservices (Spring Boot, gRPC) with CI/CD pipelines; ensured 99.9% service uptime

Selected Projects
Off-Search Ad Relevance Engine
- Role: Lead Architect & Developer
- Scope: Serve relevant ads on non-search pages (Product Detail, Home Page) at Amazon scale
- Tech: TensorFlow, Spark, Kafka, AWS Lambda, Docker, Kubernetes
- Impact: Achieved 6% uplift in off-search CTR and 8% incremental ad revenue

Real-Time CTR Prediction Pipeline
- Role: Full-Stack Engineer
- Scope: End-to-end streaming pipeline for feature computation and model inference
- Tech: Kafka, Spark Streaming, gRPC, Kubernetes, Helm
- Impact: Sustained <50 ms p99 end-to-end latency with 24/7 stability

Education
Bachelor of Science in Computer Science | Peking University
September 2015 – June 2019
- Relevant Coursework: Algorithms & Data Structures, Distributed Systems, Machine Learning, Database Systems

Certifications & Honors
- AWS Certified Solutions Architect – Associate
- TensorFlow Developer Certificate
- "Engineer of the Year" – ABC Tech Co., Ltd. (2023)

Open Source & Community
- GitHub: https://github.com/your-username
- Contributed Spark plugins and a reference Feature Store implementation
"""
    
    # 保存测试简历文件（文本格式）
    test_resume_path = "test_resume.txt"
    with open(test_resume_path, 'w', encoding='utf-8') as f:
        f.write(test_resume_content)
    
    try:
        # 初始化服务
        planner_service = PlannerAnalysisService(config.OPENAI_API_KEY)
        
        # 测试文本简历解析
        print("\n📄 测试文本简历解析...")
        resume_data = await planner_service.parse_resume(test_resume_path)
        
        print(f"\n✅ 文本简历解析结果:")
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
        
        # 保存测试结果
        test_result = {
            "resume_content": test_resume_content,
            "parsed_resume": resume_data,
            "analysis_result": analysis_result
        }
        
        with open('pdf_parsing_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(test_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 测试结果已保存到 pdf_parsing_test_result.json")
        print("\n🎉 PDF解析测试成功！")
        
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
    print("🧪 PDF解析功能测试")
    print("=" * 60)
    
    asyncio.run(test_pdf_parsing())
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60) 