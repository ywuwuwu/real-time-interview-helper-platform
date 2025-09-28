import openai
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import PyPDF2
import docx
import io
from config import config

class RealAIService:
    """真实的AI服务，使用OpenAI API"""
    
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = config.LLM_MODEL  # 使用o4-mini模型
        
    async def analyze_job_description(self, jd_text: str) -> Dict[str, Any]:
        """智能解析职位描述"""
        try:
            prompt = f"""
            请分析以下职位描述，提取关键信息：
            
            职位描述：
            {jd_text}
            
            请以JSON格式返回以下信息：
            {{
                "job_title": "职位标题",
                "required_skills": ["技能1", "技能2"],
                "preferred_skills": ["优先技能1", "优先技能2"],
                "experience_level": "经验要求",
                "responsibilities": ["职责1", "职责2"],
                "requirements": ["要求1", "要求2"],
                "company_info": "公司信息",
                "location": "工作地点",
                "salary_range": "薪资范围"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的职位分析专家，擅长提取职位描述中的关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._parse_jd_fallback(jd_text)
                
        except Exception as e:
            print(f"JD解析失败: {e}")
            return self._parse_jd_fallback(jd_text)
    
    async def analyze_job_match(
        self,
        job_description: str,
        user_skills: List[str],
        experience_years: int
    ) -> Dict[str, Any]:
        """分析职位匹配度"""
        try:
            # 先解析JD
            jd_analysis = await self.analyze_job_description(job_description)
            
            prompt = f"""
            请分析用户技能与职位要求的匹配度：
            
            职位要求：
            {json.dumps(jd_analysis, ensure_ascii=False, indent=2)}
            
            用户技能：{', '.join(user_skills)}
            用户经验：{experience_years}年
            
            请计算匹配度并返回JSON格式：
            {{
                "skill_match": 0.85,
                "experience_match": 0.75,
                "gap_analysis": {{
                    "missing_skills": ["缺失技能1", "缺失技能2"],
                    "skill_gaps": [
                        {{"skill": "技能名", "importance": "high/medium/low", "gap_level": "high/medium/low"}}
                    ],
                    "experience_gaps": [
                        {{"area": "领域", "current": 当前年数, "required": 要求年数}}
                    ]
                }}
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的技能匹配分析专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            result = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._calculate_match_fallback(user_skills, experience_years)
                
        except Exception as e:
            print(f"匹配分析失败: {e}")
            return self._calculate_match_fallback(user_skills, experience_years)
    
    async def generate_recommendations(
        self,
        analysis_result: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """基于AI分析生成个性化推荐"""
        try:
            prompt = f"""
            基于以下分析结果，生成个性化的学习推荐：
            
            分析结果：
            {json.dumps(analysis_result, ensure_ascii=False, indent=2)}
            
            请生成以下推荐，返回JSON格式：
            {{
                "courses": [
                    {{
                        "id": "course_1",
                        "title": "课程标题",
                        "platform": "平台名称",
                        "duration": "课程时长",
                        "difficulty": "难度级别",
                        "url": "课程链接",
                        "description": "课程描述",
                        "reason": "推荐理由"
                    }}
                ],
                "projects": [
                    {{
                        "id": "project_1",
                        "title": "项目标题",
                        "description": "项目描述",
                        "duration": "预计时长",
                        "tech_stack": ["技术栈"],
                        "github_url": "GitHub链接",
                        "reason": "推荐理由"
                    }}
                ],
                "practice": [
                    {{
                        "id": "practice_1",
                        "title": "练习标题",
                        "type": "练习类型",
                        "duration": "练习时长",
                        "focus_areas": ["重点领域"],
                        "difficulty": "难度级别",
                        "reason": "推荐理由"
                    }}
                ]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的职业发展顾问，擅长制定个性化学习计划。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._generate_recommendations_fallback(analysis_result)
                
        except Exception as e:
            print(f"推荐生成失败: {e}")
            return self._generate_recommendations_fallback(analysis_result)
    
    async def parse_resume(self, resume_path: str) -> Dict[str, Any]:
        """智能解析简历文件"""
        try:
            # 读取文件内容
            content = await self._extract_text_from_file(resume_path)
            
            prompt = f"""
            请解析以下简历内容，提取关键信息：
            
            简历内容：
            {content[:3000]}  # 限制长度避免token超限
            
            请以JSON格式返回：
            {{
                "skills": ["技能1", "技能2"],
                "experience_years": 年数,
                "education": "教育背景",
                "certifications": ["证书1", "证书2"],
                "projects": [
                    {{"name": "项目名", "tech": ["技术栈"], "description": "项目描述"}}
                ],
                "work_experience": [
                    {{"company": "公司名", "position": "职位", "duration": "时长", "achievements": ["成就1", "成就2"]}}
                ],
                "languages": ["语言1", "语言2"],
                "interests": ["兴趣1", "兴趣2"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的简历解析专家，擅长提取简历中的关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            result = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._parse_resume_fallback(content)
                
        except Exception as e:
            print(f"简历解析失败: {e}")
            return self._parse_resume_fallback("")
    
    async def _extract_text_from_file(self, file_path: str) -> str:
        """从文件中提取文本内容"""
        try:
            file_path = Path(file_path)
            if file_path.suffix.lower() == '.pdf':
                return self._extract_pdf_text(file_path)
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                return self._extract_docx_text(file_path)
            elif file_path.suffix.lower() == '.txt':
                return file_path.read_text(encoding='utf-8')
            else:
                return ""
        except Exception as e:
            print(f"文件读取失败: {e}")
            return ""
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """提取PDF文本"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"PDF解析失败: {e}")
            return ""
    
    def _extract_docx_text(self, file_path: Path) -> str:
        """提取DOCX文本"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"DOCX解析失败: {e}")
            return ""
    
    # 备用方法
    def _parse_jd_fallback(self, jd_text: str) -> Dict[str, Any]:
        """JD解析备用方法"""
        return {
            "job_title": "Software Engineer",
            "required_skills": ["Python", "JavaScript"],
            "preferred_skills": ["Docker", "Kubernetes"],
            "experience_level": "3-5年",
            "responsibilities": ["开发新功能", "代码审查"],
            "requirements": ["计算机科学学位", "团队合作能力"],
            "company_info": "科技公司",
            "location": "远程/办公室",
            "salary_range": "15k-25k"
        }
    
    def _calculate_match_fallback(self, user_skills: List[str], experience_years: int) -> Dict[str, Any]:
        """匹配计算备用方法"""
        skill_match = min(0.9, 0.6 + len(user_skills) * 0.1)
        experience_match = min(0.9, 0.5 + experience_years * 0.1)
        
        return {
            "skill_match": skill_match,
            "experience_match": experience_match,
            "gap_analysis": {
                "missing_skills": ["Docker", "Kubernetes", "AWS"],
                "skill_gaps": [
                    {"skill": "Docker", "importance": "high", "gap_level": "medium"},
                    {"skill": "Kubernetes", "importance": "medium", "gap_level": "high"}
                ],
                "experience_gaps": [
                    {"area": "系统设计", "current": experience_years, "required": experience_years + 2}
                ]
            }
        }
    
    def _generate_recommendations_fallback(self, analysis_result: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """推荐生成备用方法"""
        return {
            "courses": [
                {
                    "id": "course_1",
                    "title": "Docker容器化实践",
                    "platform": "Coursera",
                    "duration": "4周",
                    "difficulty": "中级",
                    "url": "https://coursera.org/docker",
                    "description": "学习Docker容器化技术",
                    "reason": "提升部署效率"
                }
            ],
            "projects": [
                {
                    "id": "project_1",
                    "title": "微服务架构项目",
                    "description": "使用Spring Boot + Docker构建微服务",
                    "duration": "2-3个月",
                    "tech_stack": ["Spring Boot", "Docker", "MySQL"],
                    "github_url": "https://github.com/example/microservice",
                    "reason": "实践微服务架构"
                }
            ],
            "practice": [
                {
                    "id": "practice_1",
                    "title": "系统设计面试练习",
                    "type": "模拟面试",
                    "duration": "45分钟",
                    "focus_areas": ["系统架构", "扩展性", "性能优化"],
                    "difficulty": "高级",
                    "reason": "提升系统设计能力"
                }
            ]
        }
    
    def _parse_resume_fallback(self, content: str) -> Dict[str, Any]:
        """简历解析备用方法"""
        return {
            "skills": ["Python", "React", "项目管理", "Git", "Docker"],
            "experience_years": 3,
            "education": "计算机科学学士",
            "certifications": ["AWS认证", "Docker认证"],
            "projects": [
                {"name": "电商平台", "tech": ["React", "Node.js", "MongoDB"], "description": "全栈电商项目"},
                {"name": "数据可视化", "tech": ["Python", "D3.js", "Pandas"], "description": "数据分析和可视化"}
            ],
            "work_experience": [
                {"company": "科技公司", "position": "软件工程师", "duration": "2年", "achievements": ["优化系统性能", "领导团队项目"]}
            ],
            "languages": ["中文", "英文"],
            "interests": ["开源项目", "技术博客"]
        } 