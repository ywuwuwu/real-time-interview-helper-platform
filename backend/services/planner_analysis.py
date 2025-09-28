import openai
from typing import Dict, List, Any, Optional
import json
import os
import re
from datetime import datetime

class PlannerAnalysisService:
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        
        # 预定义的技能分类
        self.skill_categories = {
            "programming": ["Python", "Java", "JavaScript", "C++", "Go", "Rust", "TypeScript"],
            "frontend": ["React", "Vue", "Angular", "HTML", "CSS", "JavaScript", "TypeScript"],
            "backend": ["Node.js", "Django", "Flask", "Spring", "Express", "FastAPI"],
            "database": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch"],
            "cloud": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform"],
            "mobile": ["React Native", "Flutter", "iOS", "Android", "Swift", "Kotlin"],
            "ai_ml": ["TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy"],
            "devops": ["Jenkins", "GitLab CI", "GitHub Actions", "Ansible", "Docker"],
            "soft_skills": ["项目管理", "团队协作", "沟通能力", "领导力", "问题解决"]
        }
        
        # 技能相似度映射
        self.skill_similarity_map = {
            "React": ["Vue", "Angular", "JavaScript"],
            "Vue": ["React", "Angular", "JavaScript"],
            "Angular": ["React", "Vue", "JavaScript"],
            "JavaScript": ["TypeScript", "React", "Vue"],
            "TypeScript": ["JavaScript", "React", "Vue"],
            "Python": ["Java", "C++", "Go"],
            "Java": ["Python", "C++", "Go"],
            "C++": ["Python", "Java", "Go"],
            "MySQL": ["PostgreSQL", "MongoDB", "Redis"],
            "PostgreSQL": ["MySQL", "MongoDB", "Redis"],
            "MongoDB": ["MySQL", "PostgreSQL", "Redis"],
            "AWS": ["Azure", "GCP", "Docker"],
            "Azure": ["AWS", "GCP", "Docker"],
            "GCP": ["AWS", "Azure", "Docker"],
            "Docker": ["Kubernetes", "AWS", "Azure"],
            "Kubernetes": ["Docker", "AWS", "Azure"],
            "项目管理": ["团队协作", "沟通能力", "领导力"],
            "团队协作": ["项目管理", "沟通能力", "领导力"],
            "沟通能力": ["项目管理", "团队协作", "领导力"]
        }
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """从API响应中提取JSON"""
        try:
            # 尝试直接解析
            return json.loads(response_text)
        except json.JSONDecodeError:
            # 尝试提取JSON部分
            try:
                # 查找JSON开始和结束的位置
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = response_text[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            # 如果都失败了，返回默认结构
            return {
                "required_skills": [],
                "preferred_skills": [],
                "experience_requirements": []
            }
    
    def extract_skills_from_jd(self, job_description: str) -> List[Dict[str, Any]]:
        """从JD中提取技能要求"""
        prompt = f"""
        请从以下职位描述中提取所有技能要求，并按重要性分类。
        
        职位描述：
        {job_description}
        
        请严格按照以下JSON格式返回，不要添加任何其他内容：
        {{
            "required_skills": [
                {{"skill": "Python", "importance": "high", "category": "programming"}},
                {{"skill": "React", "importance": "medium", "category": "frontend"}},
                {{"skill": "项目管理", "importance": "low", "category": "soft_skills"}}
            ],
            "preferred_skills": [
                {{"skill": "Docker", "importance": "medium", "category": "devops"}}
            ],
            "experience_requirements": [
                {{"type": "技术经验", "years": 3, "description": "后端开发经验"}},
                {{"type": "管理经验", "years": 1, "description": "团队管理经验"}}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一个专业的技能分析助手。请严格按照JSON格式返回结果，不要添加任何解释或额外内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content.strip()
            print(f"API响应: {response_text[:200]}...")  # 调试用
            
            result = self._extract_json_from_response(response_text)
            return result
        except Exception as e:
            print(f"提取技能失败: {e}")
            return self._fallback_skill_extraction(job_description)
    
    def _fallback_skill_extraction(self, job_description: str) -> Dict[str, Any]:
        """备用技能提取方法"""
        skills = []
        for category, skill_list in self.skill_categories.items():
            for skill in skill_list:
                if skill.lower() in job_description.lower():
                    skills.append({
                        "skill": skill,
                        "importance": "medium",
                        "category": category
                    })
        
        return {
            "required_skills": skills[:5],
            "preferred_skills": skills[5:8] if len(skills) > 5 else [],
            "experience_requirements": [
                {"type": "技术经验", "years": 3, "description": "相关技术经验"}
            ]
        }
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """计算语义相似度 - 增强版"""
        try:
            # 完全匹配
            if text1.lower() == text2.lower():
                return 1.0
            
            # 检查相似技能映射
            if text1 in self.skill_similarity_map:
                if text2 in self.skill_similarity_map[text1]:
                    return 0.9
            
            if text2 in self.skill_similarity_map:
                if text1 in self.skill_similarity_map[text2]:
                    return 0.9
            
            # 部分匹配（包含关系）
            if text1.lower() in text2.lower() or text2.lower() in text1.lower():
                return 0.8
            
            # 同义词匹配
            synonyms = {
                "机器学习": ["machine learning", "ml", "ai", "artificial intelligence"],
                "machine learning": ["机器学习", "ml", "ai", "artificial intelligence"],
                "python": ["python", "py"],
                "java": ["java", "jvm"],
                "scala": ["scala", "sc"],
                "sql": ["sql", "database", "mysql", "postgresql"],
                "spark": ["apache spark", "spark", "spark streaming"],
                "kafka": ["apache kafka", "kafka"],
                "tensorflow": ["tensorflow", "tf"],
                "pytorch": ["pytorch", "torch"],
                "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
                "docker": ["docker", "container"],
                "kubernetes": ["kubernetes", "k8s"],
                "aws": ["aws", "amazon web services", "amazon"],
                "distributed systems": ["分布式系统", "distributed", "microservices"],
                "分布式系统": ["distributed systems", "distributed", "microservices"],
                "大数据处理": ["big data", "data processing", "etl", "batch processing"],
                "big data": ["大数据处理", "data processing", "etl", "batch processing"],
                "a/b testing": ["ab testing", "ab test", "experiment", "实验"],
                "实验": ["a/b testing", "ab testing", "experiment"],
                "编程规范": ["coding standards", "code standards", "best practices"],
                "coding standards": ["编程规范", "code standards", "best practices"],
                "设计模式": ["design patterns", "patterns"],
                "design patterns": ["设计模式", "patterns"],
                "统计方法": ["statistics", "statistical methods", "statistical analysis"],
                "statistics": ["统计方法", "statistical methods", "statistical analysis"]
            }
            
            # 检查同义词
            for skill, synonym_list in synonyms.items():
                if text1.lower() in [skill.lower()] + [s.lower() for s in synonym_list]:
                    if text2.lower() in [skill.lower()] + [s.lower() for s in synonym_list]:
                        return 0.85
            
            # 同类别技能
            for category, skills in self.skill_categories.items():
                if text1 in skills and text2 in skills:
                    return 0.6
            
            # 关键词匹配
            keywords1 = set(text1.lower().split())
            keywords2 = set(text2.lower().split())
            if keywords1 & keywords2:  # 有交集
                return 0.4
            
            return 0.1  # 默认低相似度
        except Exception as e:
            print(f"计算相似度失败: {e}")
            return 0.5
    
    def analyze_skill_gaps(
        self, 
        jd_skills: List[Dict], 
        user_skills: List[str]
    ) -> Dict[str, Any]:
        """分析技能差距 - 增强版"""
        gaps = []
        strengths = []
        missing_skills = []
        
        # 创建用户技能的标准化版本
        normalized_user_skills = []
        for skill in user_skills:
            normalized_user_skills.append(skill.lower())
            # 添加技能的同义词
            if skill.lower() in ["tensorflow", "tf"]:
                normalized_user_skills.extend(["machine learning", "ml", "ai"])
            elif skill.lower() in ["pytorch", "torch"]:
                normalized_user_skills.extend(["machine learning", "ml", "ai"])
            elif skill.lower() in ["scikit-learn", "sklearn"]:
                normalized_user_skills.extend(["machine learning", "ml", "ai"])
            elif skill.lower() in ["apache spark", "spark"]:
                normalized_user_skills.extend(["big data", "data processing", "etl"])
            elif skill.lower() in ["kafka"]:
                normalized_user_skills.extend(["big data", "data processing", "streaming"])
            elif skill.lower() in ["hadoop"]:
                normalized_user_skills.extend(["big data", "data processing", "distributed"])
            elif skill.lower() in ["docker", "kubernetes", "k8s"]:
                normalized_user_skills.extend(["distributed systems", "microservices"])
            elif skill.lower() in ["aws", "amazon web services"]:
                normalized_user_skills.extend(["cloud", "distributed systems"])
            elif skill.lower() in ["design patterns", "patterns"]:
                normalized_user_skills.extend(["coding standards", "best practices"])
            elif skill.lower() in ["code review", "tdd"]:
                normalized_user_skills.extend(["coding standards", "best practices"])
        
        # 分析每个JD技能
        for jd_skill in jd_skills:
            skill_name = jd_skill["skill"]
            importance = jd_skill["importance"]
            normalized_jd_skill = skill_name.lower()
            
            # 检查用户是否有此技能
            if skill_name in user_skills:
                strengths.append({
                    "skill": skill_name,
                    "importance": importance,
                    "category": jd_skill.get("category", "unknown"),
                    "status": "strong"
                })
            else:
                # 计算语义相似度，看是否有相似技能
                max_similarity = 0
                similar_skill = None
                
                # 检查标准化技能
                for user_skill in normalized_user_skills:
                    similarity = self.calculate_semantic_similarity(normalized_jd_skill, user_skill)
                    if similarity > max_similarity:
                        max_similarity = similarity
                        similar_skill = user_skill
                
                # 检查原始技能
                for user_skill in user_skills:
                    similarity = self.calculate_semantic_similarity(skill_name, user_skill)
                    if similarity > max_similarity:
                        max_similarity = similarity
                        similar_skill = user_skill
                
                # 特殊技能映射检查
                skill_mappings = {
                    "机器学习算法": ["tensorflow", "pytorch", "scikit-learn", "mlflow", "machine learning", "ml", "ai", "深度学习", "神经网络", "machine learning"],
                    "统计方法": ["statistics", "statistical", "data analysis", "analytics", "统计", "数据分析", "statistics"],
                    "分布式系统": ["distributed", "microservices", "docker", "kubernetes", "k8s", "scaling", "分布式", "微服务", "distributed systems"],
                    "大数据处理": ["spark", "kafka", "hadoop", "big data", "etl", "data processing", "大数据", "数据处理", "data pipelines"],
                    "a/b测试": ["ab testing", "experiment", "testing", "实验", "a/b test", "a/b testing"],
                    "实验设计": ["experiment", "testing", "ab testing", "实验", "实验设计"],
                    "编程规范": ["coding standards", "code review", "tdd", "best practices", "design patterns", "编程规范", "代码规范"],
                    "设计模式": ["design patterns", "patterns", "architecture", "coding standards", "设计模式", "架构模式"],
                    "software development": ["python", "java", "scala", "programming", "coding", "软件开发", "编程", "software development"],
                    "machine learning": ["tensorflow", "pytorch", "scikit-learn", "ml", "ai", "机器学习", "深度学习", "machine learning"],
                    "data pipelines": ["spark", "kafka", "hadoop", "etl", "data processing", "数据管道", "数据处理", "data pipelines"],
                    "distributed systems": ["docker", "kubernetes", "microservices", "分布式", "微服务", "distributed systems"],
                    "coding standards": ["code review", "tdd", "best practices", "编程规范", "代码规范"],
                    "design patterns": ["patterns", "architecture", "设计模式", "架构模式"],
                    "a/b testing": ["experiment", "testing", "实验", "ab test", "a/b testing"],
                    "statistics": ["statistical", "data analysis", "analytics", "统计", "数据分析", "statistics"],
                    "information retrieval": ["search", "elasticsearch", "solr", "信息检索", "搜索", "information retrieval"],
                    "natural language processing": ["nlp", "text processing", "language model", "自然语言处理", "文本处理"],
                    "system design": ["architecture", "design", "系统设计", "架构设计", "system design"],
                    "programming languages": ["python", "java", "scala", "programming", "编程语言", "programming languages"]
                }
                
                # 检查特殊映射
                if skill_name in skill_mappings:
                    for mapped_skill in skill_mappings[skill_name]:
                        if mapped_skill in normalized_user_skills:
                            max_similarity = 0.8
                            similar_skill = mapped_skill
                            break
                
                if max_similarity > 0.6:  # 相似度阈值
                    gaps.append({
                        "skill": skill_name,
                        "similar_skill": similar_skill,
                        "similarity": max_similarity,
                        "importance": importance,
                        "category": jd_skill.get("category", "unknown"),
                        "status": "partial",
                        "priority": "medium" if importance == "high" else "low"
                    })
                else:
                    gaps.append({
                        "skill": skill_name,
                        "importance": importance,
                        "category": jd_skill.get("category", "unknown"),
                        "status": "missing",
                        "priority": "high" if importance == "high" else "medium"
                    })
                    missing_skills.append(skill_name)
        
        return {
            "gaps": gaps,
            "strengths": strengths,
            "missing_skills": missing_skills,
            "gap_count": len(gaps),
            "strength_count": len(strengths)
        }
    
    async def analyze_job_match(
        self, 
        job_description: str, 
        user_skills: List[str], 
        experience_years: int
    ) -> Dict[str, Any]:
        """分析JD与用户能力的匹配度 - 增强版"""
        
        # 1. 提取JD技能要求
        jd_analysis = self.extract_skills_from_jd(job_description)
        
        # 2. 分析技能差距
        skill_analysis = self.analyze_skill_gaps(
            jd_analysis["required_skills"], 
            user_skills
        )
        
        # 3. 计算匹配度
        total_skills = len(jd_analysis["required_skills"])
        matched_skills = len(skill_analysis["strengths"])
        skill_match_percentage = (matched_skills / total_skills * 100) if total_skills > 0 else 0
        
        # 4. 经验匹配分析
        experience_requirements = jd_analysis.get("experience_requirements", [])
        experience_match_percentage = self._calculate_experience_match(
            experience_requirements, experience_years
        )
        
        # 5. 生成详细分析报告
        detailed_analysis = await self._generate_detailed_analysis(
            job_description, user_skills, experience_years, skill_analysis, jd_analysis
        )
        
        return {
            "skill_match": round(skill_match_percentage, 1),
            "experience_match": round(experience_match_percentage, 1),
            "overall_match": round((skill_match_percentage + experience_match_percentage) / 2, 1),
            "gaps": skill_analysis["gaps"],
            "strengths": skill_analysis["strengths"],
            "missing_skills": skill_analysis["missing_skills"],
            "jd_requirements": jd_analysis,
            "detailed_analysis": detailed_analysis,
            "improvement_priorities": self._generate_improvement_priorities(skill_analysis),
            "timeline_estimate": self._estimate_improvement_timeline(skill_analysis),
            "confidence_score": self._calculate_confidence_score(skill_analysis, experience_years)
        }
    
    def _calculate_experience_match(
        self, 
        requirements: List[Dict], 
        user_years: int
    ) -> float:
        """计算经验匹配度"""
        if not requirements:
            return 70.0  # 默认匹配度
        
        total_required_years = sum(req.get("years", 0) for req in requirements)
        avg_required_years = total_required_years / len(requirements)
        
        if user_years >= avg_required_years:
            return min(100.0, 70 + (user_years - avg_required_years) * 10)
        else:
            return max(0.0, 70 - (avg_required_years - user_years) * 15)
    
    async def _generate_detailed_analysis(
        self, 
        job_description: str, 
        user_skills: List[str], 
        experience_years: int,
        skill_analysis: Dict,
        jd_analysis: Dict
    ) -> Dict[str, Any]:
        """生成详细分析报告"""
        
        prompt = f"""
        基于以下信息，生成详细的职位匹配分析报告。
        
        职位描述：{job_description}
        用户技能：{', '.join(user_skills)}
        工作经验：{experience_years}年
        
        技能差距分析：{json.dumps(skill_analysis, ensure_ascii=False)}
        JD要求分析：{json.dumps(jd_analysis, ensure_ascii=False)}
        
        请严格按照以下JSON格式返回，不要添加任何其他内容：
        {{
            "core_competencies": ["技能1", "技能2"],
            "main_gaps": ["差距1", "差距2"],
            "short_term_goals": ["目标1", "目标2"],
            "medium_term_goals": ["目标1", "目标2"],
            "long_term_goals": ["目标1", "目标2"],
            "risk_assessment": "风险评估描述",
            "market_positioning": "市场定位建议"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一个专业的职业分析助手。请严格按照JSON格式返回结果，不要添加任何解释或额外内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            response_text = response.choices[0].message.content.strip()
            print(f"详细分析API响应: {response_text[:200]}...")  # 调试用
            
            result = self._extract_json_from_response(response_text)
            return result
        except Exception as e:
            print(f"生成详细分析失败: {e}")
            return self._fallback_detailed_analysis(skill_analysis)
    
    def _fallback_detailed_analysis(self, skill_analysis: Dict) -> Dict[str, Any]:
        """备用详细分析"""
        return {
            "core_competencies": ["技术能力", "问题解决"],
            "main_gaps": ["技能差距", "经验不足"],
            "short_term_goals": ["学习新技能", "项目实践"],
            "medium_term_goals": ["技能提升", "经验积累"],
            "long_term_goals": ["职业发展", "技能深化"],
            "risk_assessment": "需要持续学习和实践",
            "market_positioning": "技术专家方向"
        }
    
    def _generate_improvement_priorities(self, skill_analysis: Dict) -> List[Dict[str, Any]]:
        """生成改进优先级"""
        priorities = []
        
        for gap in skill_analysis["gaps"]:
            priority_score = 0
            if gap["importance"] == "high":
                priority_score += 3
            elif gap["importance"] == "medium":
                priority_score += 2
            else:
                priority_score += 1
            
            if gap["status"] == "missing":
                priority_score += 2
            elif gap["status"] == "partial":
                priority_score += 1
            
            priorities.append({
                "skill": gap["skill"],
                "priority_score": priority_score,
                "estimated_time": "2-4周" if gap["status"] == "partial" else "1-3个月",
                "learning_path": self._generate_learning_path(gap["skill"], gap["category"])
            })
        
        # 按优先级排序
        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        return priorities[:5]  # 返回前5个优先级
    
    def _generate_learning_path(self, skill: str, category: str) -> List[str]:
        """生成学习路径"""
        learning_paths = {
            "programming": [
                f"学习{skill}基础语法",
                f"完成{skill}小项目",
                f"参与{skill}开源项目"
            ],
            "frontend": [
                f"学习{skill}框架基础",
                f"构建{skill}项目",
                f"优化{skill}性能"
            ],
            "backend": [
                f"学习{skill}框架",
                f"构建API服务",
                f"部署{skill}应用"
            ],
            "database": [
                f"学习{skill}基础",
                f"设计数据库架构",
                f"优化{skill}性能"
            ],
            "cloud": [
                f"学习{skill}基础概念",
                f"完成{skill}认证",
                f"实践{skill}项目"
            ]
        }
        
        return learning_paths.get(category, [
            f"学习{skill}基础",
            f"实践{skill}项目",
            f"深入{skill}高级特性"
        ])
    
    def _estimate_improvement_timeline(self, skill_analysis: Dict) -> Dict[str, Any]:
        """估算改进时间线"""
        high_priority_gaps = [gap for gap in skill_analysis["gaps"] if gap["priority"] == "high"]
        medium_priority_gaps = [gap for gap in skill_analysis["gaps"] if gap["priority"] == "medium"]
        
        total_weeks = len(high_priority_gaps) * 8 + len(medium_priority_gaps) * 4
        
        return {
            "total_weeks": total_weeks,
            "high_priority_weeks": len(high_priority_gaps) * 8,
            "medium_priority_weeks": len(medium_priority_gaps) * 4,
            "estimated_completion_date": self._calculate_completion_date(total_weeks),
            "milestones": self._generate_milestones(skill_analysis["gaps"])
        }
    
    def _calculate_completion_date(self, weeks: int) -> str:
        """计算预计完成日期"""
        from datetime import datetime, timedelta
        completion_date = datetime.now() + timedelta(weeks=weeks)
        return completion_date.strftime("%Y-%m-%d")
    
    def _generate_milestones(self, gaps: List[Dict]) -> List[Dict[str, Any]]:
        """生成里程碑"""
        milestones = []
        current_week = 0
        
        for gap in gaps:
            weeks_needed = 8 if gap["priority"] == "high" else 4
            current_week += weeks_needed
            
            milestones.append({
                "skill": gap["skill"],
                "week": current_week,
                "description": f"掌握{gap['skill']}技能",
                "priority": gap["priority"]
            })
        
        return milestones
    
    def _calculate_confidence_score(self, skill_analysis: Dict, experience_years: int) -> float:
        """计算置信度分数"""
        # 基于技能差距数量和经验年数计算置信度
        gap_count = len(skill_analysis["gaps"])
        strength_count = len(skill_analysis["strengths"])
        
        # 基础分数
        base_score = 70.0
        
        # 技能匹配度影响
        if strength_count > gap_count:
            base_score += 15
        elif gap_count > strength_count * 2:
            base_score -= 20
        
        # 经验影响
        if experience_years >= 5:
            base_score += 10
        elif experience_years < 2:
            base_score -= 10
        
        return max(0.0, min(100.0, base_score))

    async def generate_recommendations(
        self, 
        analysis_result: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """生成个性化推荐 - 基于真实技能差距分析"""
        
        # 提取关键信息
        gaps = analysis_result.get('gaps', [])
        strengths = analysis_result.get('strengths', [])
        skill_match = analysis_result.get('skill_match', 0)
        experience_match = analysis_result.get('experience_match', 0)
        
        # 按优先级分类技能差距
        high_priority_gaps = [gap for gap in gaps if gap.get('priority') == 'high']
        medium_priority_gaps = [gap for gap in gaps if gap.get('priority') == 'medium']
        low_priority_gaps = [gap for gap in gaps if gap.get('priority') == 'low']
        
        prompt = f"""
        基于以下详细的技能分析结果，生成个性化的学习和发展建议。
        
        分析结果：
        - 技能匹配度: {skill_match}%
        - 经验匹配度: {experience_match}%
        - 整体匹配度: {analysis_result.get('overall_match', 0)}%
        
        技能差距分析：
        - 高优先级差距 ({len(high_priority_gaps)}项): {[gap['skill'] for gap in high_priority_gaps]}
        - 中优先级差距 ({len(medium_priority_gaps)}项): {[gap['skill'] for gap in medium_priority_gaps]}
        - 低优先级差距 ({len(low_priority_gaps)}项): {[gap['skill'] for gap in low_priority_gaps]}
        
        技能优势：
        - 匹配技能 ({len(strengths)}项): {[strength['skill'] for strength in strengths]}
        
        请基于以上分析，生成针对性的推荐，重点关注：
        1. 优先推荐高优先级技能差距的课程
        2. 项目练习应该结合用户现有技能和需要提升的技能
        3. 模拟面试应该针对目标岗位的具体要求
        4. 考虑用户的经验水平和学习时间
        
        请严格按照以下JSON格式返回，不要添加任何其他内容：
        {{
            "courses": [
                {{
                    "id": "course_1",
                    "name": "课程名称",
                    "platform": "平台名称",
                    "difficulty": "初级/中级/高级",
                    "duration": "学习时长",
                    "url": "课程链接",
                    "description": "课程描述",
                    "target_skill": "目标技能",
                    "priority": "high/medium/low"
                }}
            ],
            "projects": [
                {{
                    "id": "project_1",
                    "name": "项目名称",
                    "tech_stack": ["技术栈"],
                    "difficulty": "初级/中级/高级",
                    "duration": "项目时长",
                    "description": "项目描述",
                    "learning_objectives": ["学习目标"],
                    "target_skills": ["目标技能"]
                }}
            ],
            "practice": [
                {{
                    "id": "practice_1",
                    "type": "练习类型",
                    "frequency": "练习频率",
                    "focus": "重点内容",
                    "description": "练习描述",
                    "target_skills": ["目标技能"]
                }}
            ],
            "learning_path": {{
                "short_term": ["短期目标"],
                "medium_term": ["中期目标"],
                "long_term": ["长期目标"]
            }},
            "timeline": {{
                "estimated_weeks": 数字,
                "milestones": ["里程碑"]
            }}
        }}
        
        注意：
        1. 课程应该针对具体的技能差距
        2. 项目应该结合用户现有技能和新技能
        3. 练习应该针对面试要求
        4. 学习路径应该有明确的阶段性目标
        5. 时间线要现实可行
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一个专业的职业发展顾问和技能提升专家。请基于用户的技能差距分析，生成具体、可执行的个性化推荐。确保推荐内容针对性强、实用性强。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            response_text = response.choices[0].message.content.strip()
            print(f"🔍 AI推荐生成响应: {response_text[:300]}...")
            
            result = self._extract_json_from_response(response_text)
            
            # 确保返回的数据结构正确
            if not result.get("courses"):
                result["courses"] = []
            if not result.get("projects"):
                result["projects"] = []
            if not result.get("practice"):
                result["practice"] = []
            if not result.get("learning_path"):
                result["learning_path"] = {"short_term": [], "medium_term": [], "long_term": []}
            if not result.get("timeline"):
                result["timeline"] = {"estimated_weeks": 12, "milestones": []}
            
            print(f"✅ 个性化推荐生成完成:")
            print(f"  - 推荐课程: {len(result['courses'])} 项")
            print(f"  - 推荐项目: {len(result['projects'])} 项")
            print(f"  - 推荐练习: {len(result['practice'])} 项")
            print(f"  - 学习路径: {len(result['learning_path']['short_term'])} 短期目标")
            print(f"  - 预计时间: {result['timeline']['estimated_weeks']} 周")
            
            return result
            
        except Exception as e:
            print(f"❌ AI推荐生成失败: {e}")
            # 返回基于技能差距的智能默认推荐
            return self._generate_smart_fallback_recommendations(analysis_result)
    
    def _generate_smart_fallback_recommendations(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成智能的备用推荐"""
        gaps = analysis_result.get('gaps', [])
        skill_match = analysis_result.get('skill_match', 0)
        
        # 基于技能差距生成推荐
        courses = []
        projects = []
        practice = []
        
        # 课程推荐
        if any('machine learning' in gap['skill'].lower() for gap in gaps):
            courses.append({
                "id": "course_ml",
                "name": "机器学习基础 - Coursera",
                "platform": "Coursera",
                "difficulty": "中级",
                "duration": "8周",
                "url": "https://www.coursera.org/learn/machine-learning",
                "description": "吴恩达教授的经典机器学习课程",
                "target_skill": "Machine Learning",
                "priority": "high"
            })
        
        if any('python' in gap['skill'].lower() for gap in gaps):
            courses.append({
                "id": "course_python",
                "name": "Python编程基础 - Codecademy",
                "platform": "Codecademy",
                "difficulty": "初级",
                "duration": "3周",
                "url": "https://www.codecademy.com/learn/learn-python-3",
                "description": "从零开始学习Python编程",
                "target_skill": "Python",
                "priority": "high"
            })
        
        if any('system design' in gap['skill'].lower() for gap in gaps):
            courses.append({
                "id": "course_system_design",
                "name": "系统设计面试准备 - Educative",
                "platform": "Educative",
                "difficulty": "高级",
                "duration": "6周",
                "url": "https://www.educative.io/courses/grokking-the-system-design-interview",
                "description": "专门针对系统设计面试的课程",
                "target_skill": "System Design",
                "priority": "high"
            })
        
        # 项目推荐
        if skill_match < 50:
            projects.append({
                "id": "project_basic",
                "name": "全栈Web应用开发",
                "tech_stack": ["React", "Node.js", "MongoDB"],
                "difficulty": "中级",
                "duration": "4-6周",
                "description": "开发一个完整的Web应用，涵盖前后端开发",
                "learning_objectives": ["掌握全栈开发", "学习数据库设计", "理解API开发"],
                "target_skills": ["React", "Node.js", "MongoDB"]
            })
        
        # 练习推荐
        practice.append({
            "id": "practice_coding",
            "type": "编程练习",
            "frequency": "每周3次",
            "focus": "算法和数据结构",
            "description": "在LeetCode上练习编程题，重点练习目标岗位相关的算法",
            "target_skills": ["算法", "数据结构", "编程"]
        })
        
        practice.append({
            "id": "practice_interview",
            "type": "模拟面试",
            "frequency": "每周1次",
            "focus": "技术面试和系统设计",
            "description": "模拟真实面试环境，练习技术问题回答",
            "target_skills": ["面试技巧", "技术表达", "系统设计"]
        })
        
        return {
            "courses": courses,
            "projects": projects,
            "practice": practice,
            "learning_path": {
                "short_term": ["掌握基础编程技能", "学习核心算法"],
                "medium_term": ["完成实战项目", "提升系统设计能力"],
                "long_term": ["达到目标岗位要求", "准备面试"]
            },
            "timeline": {
                "estimated_weeks": 12,
                "milestones": ["第4周完成基础课程", "第8周完成项目", "第12周准备面试"]
            }
        }
    
    async def parse_resume(self, resume_path: str) -> Dict[str, Any]:
        """解析简历内容 - 简化版，直接让GPT分析"""
        try:
            print(f"📄 开始解析简历: {resume_path}")
            
            # 1. 提取简历文本内容
            resume_content = await self._extract_resume_text(resume_path)
            if not resume_content:
                error_msg = f"❌ 简历文本提取失败: {resume_path}"
                print(error_msg)
                print("💡 建议:")
                print("  1. 确保PDF文件没有损坏")
                print("  2. 尝试将PDF转换为文本文件")
                print("  3. 检查文件编码格式")
                print("  4. 确保PyPDF2库已正确安装: pip install PyPDF2==3.0.1")
                raise ValueError(error_msg)
            
            print(f"📝 简历内容长度: {len(resume_content)} 字符")
            
            # 检查内容是否太短
            if len(resume_content.strip()) < 50:
                error_msg = f"❌ 简历内容过短，可能提取失败: {len(resume_content)} 字符"
                print(error_msg)
                print("💡 建议:")
                print("  1. 检查PDF文件是否包含文本内容")
                print("  2. 尝试使用其他PDF阅读器打开文件")
                print("  3. 将PDF转换为文本文件后重试")
                raise ValueError(error_msg)
            
            # 2. 直接让GPT分析整个简历
            prompt = f"""
            请分析以下简历，提取关键信息并进行详细的技能分析。

            简历内容：
            {resume_content}

            请提供以下分析：

            1. 技能清单（包括技术技能、软技能、工具等）
            2. 工作经验年数
            3. 教育背景
            4. 项目经验
            5. 技能分类（编程语言、框架、工具、软技能等）
            6. 技能熟练度评估（初级/中级/高级）

            请以JSON格式返回，格式如下：
            {{
                "skills": ["技能1", "技能2", "技能3"],
                "experience_years": 数字,
                "education": "学历信息",
                "projects": ["项目1", "项目2"],
                "languages": ["语言1", "语言2"],
                "certifications": ["认证1", "认证2"],
                "skill_categories": {{
                    "programming_languages": ["Python", "Java"],
                    "frameworks": ["React", "Django"],
                    "tools": ["Git", "Docker"],
                    "soft_skills": ["项目管理", "团队协作"]
                }},
                "skill_levels": {{
                    "Python": "高级",
                    "React": "中级",
                    "项目管理": "高级"
                }},
                "detailed_analysis": "详细的技能分析说明"
            }}

            注意：
            1. 提取所有相关的技术技能，包括编程语言、框架、工具、平台等
            2. 准确计算工作经验年数
            3. 对技能进行合理分类
            4. 评估技能熟练度
            5. 提供详细的分析说明
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一个专业的简历分析专家。请仔细分析简历内容，提取准确的信息，并提供详细的技能分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            response_text = response.choices[0].message.content.strip()
            print(f"🔍 GPT分析响应: {response_text[:300]}...")
            
            result = self._extract_json_from_response(response_text)
            
            # 确保返回的数据结构正确
            if not result.get("skills"):
                result["skills"] = []
            if not result.get("experience_years"):
                result["experience_years"] = 0
            if not result.get("education"):
                result["education"] = "未指定"
            if not result.get("projects"):
                result["projects"] = []
            if not result.get("languages"):
                result["languages"] = ["中文", "英文"]
            if not result.get("certifications"):
                result["certifications"] = []
            if not result.get("skill_categories"):
                result["skill_categories"] = {}
            if not result.get("skill_levels"):
                result["skill_levels"] = {}
            if not result.get("detailed_analysis"):
                result["detailed_analysis"] = "技能分析完成"
            
            print(f"✅ 简历解析完成:")
            print(f"  - 提取技能: {result['skills']}")
            print(f"  - 工作经验: {result['experience_years']} 年")
            print(f"  - 学历: {result['education']}")
            print(f"  - 项目: {result['projects']}")
            print(f"  - 技能分类: {result.get('skill_categories', {})}")
            print(f"  - 技能等级: {result.get('skill_levels', {})}")
            print(f"  - 详细分析: {result.get('detailed_analysis', '')[:100]}...")
            
            return result
            
        except Exception as e:
            error_msg = f"❌ 简历解析失败: {e}"
            print(error_msg)
            print("💡 解决方案:")
            print("  1. 检查文件格式是否支持")
            print("  2. 确保文件没有损坏")
            print("  3. 尝试使用文本格式的简历")
            print("  4. 检查网络连接和API密钥")
            raise ValueError(error_msg)
    
    async def _extract_resume_text(self, resume_path: str) -> str:
        """提取简历文本内容"""
        try:
            file_extension = resume_path.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                print("📄 检测到PDF文件，提取文本...")
                try:
                    import PyPDF2
                    resume_content = ""
                    with open(resume_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        print(f"✅ PDF文件读取成功，页数: {len(pdf_reader.pages)}")
                        for i, page in enumerate(pdf_reader.pages):
                            page_text = page.extract_text()
                            resume_content += page_text + "\n"
                            print(f"✅ 第{i+1}页提取成功，长度: {len(page_text)} 字符")
                    print(f"✅ PDF文本提取成功，总长度: {len(resume_content)} 字符")
                    return resume_content
                except ImportError as e:
                    print(f"⚠️ PyPDF2导入失败: {e}")
                    return None
                except Exception as e:
                    print(f"❌ PDF解析失败: {e}")
                    return None
            else:
                # 对于文本文件，尝试多种编码
                encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
                
                for encoding in encodings:
                    try:
                        with open(resume_path, 'r', encoding=encoding) as f:
                            resume_content = f.read()
                        print(f"✅ 使用 {encoding} 编码成功读取文件")
                        return resume_content
                    except UnicodeDecodeError:
                        print(f"⚠️ {encoding} 编码失败，尝试下一个...")
                        continue
                
                print("❌ 所有编码都失败")
                return None
                
        except Exception as e:
            print(f"❌ 文本提取失败: {e}")
            return None
    
    def _get_default_resume_data(self) -> Dict[str, Any]:
        """返回默认的简历数据"""
        return {
            "skills": ["Python", "React", "项目管理", "Git", "Docker"],
            "experience_years": 3,
            "education": "计算机科学学士",
            "projects": ["电商平台", "移动应用", "数据分析系统"],
            "languages": ["中文", "英文"],
            "certifications": ["AWS认证", "PMP认证"]
        } 