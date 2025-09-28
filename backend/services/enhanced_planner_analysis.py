import openai
from typing import Dict, List, Any, Optional
import json
import re
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime

class EnhancedPlannerAnalysisService:
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        # 初始化语义嵌入模型
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
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
    
    def extract_skills_from_jd(self, job_description: str) -> List[Dict[str, Any]]:
        """从JD中提取技能要求"""
        prompt = f"""
        请从以下职位描述中提取所有技能要求，并按重要性分类：
        
        职位描述：
        {job_description}
        
        请以JSON格式返回，格式如下：
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
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
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
        """计算语义相似度"""
        try:
            embeddings = self.embedding_model.encode([text1, text2])
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            return float(similarity)
        except Exception as e:
            print(f"计算相似度失败: {e}")
            return 0.5
    
    def analyze_skill_gaps(
        self, 
        jd_skills: List[Dict], 
        user_skills: List[str]
    ) -> Dict[str, Any]:
        """分析技能差距"""
        gaps = []
        strengths = []
        missing_skills = []
        
        # 分析每个JD技能
        for jd_skill in jd_skills:
            skill_name = jd_skill["skill"]
            importance = jd_skill["importance"]
            
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
                
                for user_skill in user_skills:
                    similarity = self.calculate_semantic_similarity(skill_name, user_skill)
                    if similarity > max_similarity:
                        max_similarity = similarity
                        similar_skill = user_skill
                
                if max_similarity > 0.7:  # 相似度阈值
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
    
    async def enhanced_job_match_analysis(
        self, 
        job_description: str, 
        user_skills: List[str], 
        experience_years: int,
        user_resume: Optional[str] = None
    ) -> Dict[str, Any]:
        """增强的职位匹配分析"""
        
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
        基于以下信息，生成详细的职位匹配分析报告：
        
        职位描述：{job_description}
        用户技能：{', '.join(user_skills)}
        工作经验：{experience_years}年
        
        技能差距分析：{json.dumps(skill_analysis, ensure_ascii=False)}
        JD要求分析：{json.dumps(jd_analysis, ensure_ascii=False)}
        
        请提供：
        1. 核心竞争力分析
        2. 主要差距分析
        3. 短期改进建议（1-3个月）
        4. 中期发展建议（3-6个月）
        5. 长期职业规划建议（6-12个月）
        6. 风险评估
        
        以JSON格式返回，格式如下：
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
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
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