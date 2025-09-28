# rag_pipeline.py — Version 1.1.1
# =============================================================================
# Interview Helper Backend — RAG Pipeline & AI Interview Logic
#
# Overview:
#   - Implements the core Retrieval-Augmented Generation (RAG) pipeline for mock interview sessions.
#   - Handles context construction, prompt engineering, and OpenAI LLM calls for dynamic Q&A.
#   - Parses and structures AI responses, feedback, and improvement suggestions for each interview turn.
#   - Includes robust error handling for non-JSON LLM outputs.
#
# Main Classes & Functions:
#   1. InterviewContext   — Data structure for job info, JD, interview type, and session history.
#   2. RAGPipeline        — Main pipeline for generating AI interview questions, feedback, and suggestions.
#      - generate_response(user_input, context): Core method to interact with the LLM and parse results.
#      - generate_gpt_advice(prompt): Generates preparation advice based on job description.
#
# Usage:
#   - Instantiated and used in backend/app.py as `rag_pipeline`.
#   - Called in the /api/rag and /api/jd_advice endpoints to process user input and generate AI-driven interview content.
#
# Dependencies:
#   - OpenAI API          : Large-language-model Q&A
#   - Python dataclasses  : Context management
#   - numpy, re, json     : Feedback analysis and parsing
#
# Author: BeeBee AI Track-B
# Version: 1.1.1
# =============================================================================

import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from pathlib import Path
import re
from openai import OpenAI
from config import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

def chat_completion(model_name, messages, temperature, max_tokens):
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content


@dataclass
class InterviewContext:
    """Context for the interview session"""
    job_title: str
    job_description: Optional[str] = None
    company: Optional[str] = None
    interview_type: str = "behavioral"
    session_history: List[Dict] | None = None
    
    def __post_init__(self):
        if self.session_history is None:
            self.session_history = []

class FeedbackAnalyzer:
    """Analyze user responses and generate feedback"""
    
    def __init__(self):
        self.star_keywords = {
            "situation": ["situation", "context", "background", "when", "where"],
            "task": ["task", "goal", "objective", "responsibility", "challenge"],
            "action": ["action", "did", "implemented", "developed", "created"],
            "result": ["result", "outcome", "impact", "achieved", "success"]
        }
    
    def analyze_structure(self, response: str) -> Dict[str, float]:
        """Analyze if response follows STAR method"""
        response_lower = response.lower()
        scores = {}
        
        for component, keywords in self.star_keywords.items():
            found = any(keyword in response_lower for keyword in keywords)
            scores[component] = 1.0 if found else 0.0
        
        overall_structure = sum(scores.values()) / len(scores)
        scores["overall"] = overall_structure
        return scores
    
    def analyze_clarity(self, response: str) -> float:
        """Analyze response clarity"""
        # Simple heuristics for clarity
        sentences = response.split('.')
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        
        # Ideal sentence length is between 15-20 words
        if 15 <= avg_sentence_length <= 20:
            clarity_score = 1.0
        elif 10 <= avg_sentence_length <= 25:
            clarity_score = 0.8
        else:
            clarity_score = 0.6
            
        return clarity_score
    
    def analyze_specificity(self, response: str) -> float:
        """Check for specific examples and metrics"""
        specificity_indicators = [
            r'\d+%',  # Percentages
            r'\$\d+',  # Dollar amounts
            r'\d+ (days|weeks|months|years)',  # Time periods
            r'increased|decreased|improved|reduced by',  # Impact words
            r'team of \d+',  # Team sizes
            r'project|initiative|campaign'  # Specific work examples
        ]
        
        matches = sum(1 for pattern in specificity_indicators 
                     if re.search(pattern, response, re.IGNORECASE))
        
        return min(matches / 3, 1.0)  # Normalize to 0-1

class RAGPipeline:
    """Main RAG pipeline for interview processing"""
    def generate_gpt_advice(self, prompt: str, model: str = "gpt-4o-mini") -> str:
        model_name = model or config.LLM_MODEL    # 优先用传参，否则用配置中的模型
        messages = [
            {"role": "system", "content": "你是一名专业的AI面试教练，善于根据岗位描述为候选人提供详细的面试准备建议。"},
            {"role": "user", "content": prompt}
        ]
        content = chat_completion(model_name, messages, 0.7, 512)
        return content if content else ""
    
    def __init__(self, knowledge_base_path: Path | None = None):
        self.knowledge_base_path = knowledge_base_path
        self.feedback_analyzer = FeedbackAnalyzer()
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict:
        """Load job-specific knowledge base"""
        # Mock knowledge base - in production, load from files/database
        return {
            "software-engineer": {
                "key_skills": ["problem-solving", "coding", "system design", "collaboration"],
                "common_scenarios": [
                    "debugging complex issues",
                    "optimizing performance",
                    "working with legacy code",
                    "leading technical initiatives"
                ],
                "follow_up_questions": [
                    "What technologies did you use?",
                    "How did you measure the impact?",
                    "What challenges did you face?",
                    "How did you collaborate with the team?"
                ]
            },
            "data-scientist": {
                "key_skills": ["analysis", "machine learning", "statistics", "communication"],
                "common_scenarios": [
                    "building predictive models",
                    "data cleaning and preprocessing",
                    "presenting insights to stakeholders",
                    "A/B testing and experimentation"
                ],
                "follow_up_questions": [
                    "What algorithms did you consider?",
                    "How did you validate your model?",
                    "What was the business impact?",
                    "How did you handle missing data?"
                ]
            },
            "product-manager": {
                "key_skills": ["strategy", "prioritization", "communication", "analytics"],
                "common_scenarios": [
                    "launching new features",
                    "managing stakeholder expectations",
                    "making data-driven decisions",
                    "handling competing priorities"
                ],
                "follow_up_questions": [
                    "How did you measure success?",
                    "Who were your key stakeholders?",
                    "What trade-offs did you make?",
                    "How did you validate the need?"
                ]
            }
        }
    
    def generate_response(self, user_input: str, context: InterviewContext) -> Tuple[str, Dict]:
        """
        用GPT-4o-mini定制化面试：
        - prompt包含JD（如有）、历史对话、用户最新回答
        - GPT输出下一个AI问题、反馈、改进建议
        """
        # 构造历史对话文本
        history_text = ""
        if context.session_history:
            for turn in context.session_history:
                q = turn.get("question", "")
                a = turn.get("user_response", "")
                history_text += f"面试官: {q}\n候选人: {a}\n"
        # 构造主prompt
        if context.job_description:
            system_prompt = (
                "你是一名专业的AI面试官。请严格根据下面的岗位描述（JD）和历史对话与候选人互动。"
                "如果用户的问题与岗位描述（JD）相关（如岗位名称、职责、要求、待遇、公司信息等），请直接引用JD内容用中文简明准确地回答用户问题，不要重复JD原文，要用自己的话总结。"
                "如果用户的问题与JD无关或是常规面试流程，请继续结构化面试，提出下一个面试问题，并对候选人的最新回答给出结构化反馈（包括结构、内容、表达、相关性等）和改进建议。"
                "每轮请用JSON格式输出，字段包括question（下一个问题或JD相关问题的直接回答）、feedback（结构化反馈）、improvements（改进建议）。"
                "无论用户用什么语言提问，都必须严格只输出JSON格式"
            )
            user_prompt = (
                f"岗位描述（JD）：\n{context.job_description}\n\n"
                f"历史对话：\n{history_text}"
                f"候选人最新输入：{user_input}"
            )
        else:
            system_prompt = (
                "你是一名AI面试官，请根据历史对话，继续进行结构化面试。"
                "每轮请输出下一个面试问题，并对候选人的最新回答给出结构化反馈和改进建议。"
                "请用JSON格式输出，字段包括question, feedback, improvements。"
            )
            user_prompt = (
                f"历史对话：\n{history_text}"
                f"候选人最新输入：{user_input}"
            )
        # 调用GPT-4o-mini
        model_name = "gpt-4o-mini"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        gpt_output = chat_completion(model_name, messages, 0.7, 512)
        # 解析GPT输出
        import json
        ai_response = "AI未返回问题。"
        feedback = {}
        improvements = []
        try:
            if not isinstance(gpt_output, str):
                gpt_output = str(gpt_output)
            # --- 新增：自动去除markdown的json包裹 ---
            if gpt_output.strip().startswith("```json"):
                gpt_output = gpt_output.strip()[7:]
                if gpt_output.endswith("```"):
                    gpt_output = gpt_output[:-3].strip()
            # --- end ---

            parsed = json.loads(gpt_output)
            ai_response = parsed.get("question") or "AI未返回问题。"
            feedback = parsed.get("feedback") or {}
            improvements = parsed.get("improvements") or []
        except Exception:
            print("GPT输出内容无法解析为JSON，原始内容：", gpt_output)
            if isinstance(gpt_output, str):
                ai_response = gpt_output
            else:
                ai_response = "AI未返回问题。"
            feedback = {}
            improvements = []
        # *** 这里加类型补丁 ***
        if not isinstance(feedback, dict):
            feedback = {"general": str(feedback)}
        if not isinstance(improvements, list):
            improvements = [str(improvements)]
        # 评分可后续扩展
        return ai_response, {
            "feedback": feedback,
            "suggested_improvements": improvements,
            "score": None
        }
    
    def _generate_follow_up(self, 
                           user_input: str, 
                           context: InterviewContext,
                           job_context: Dict) -> str:
        """Generate contextual follow-up question"""
        
        # Check conversation depth
        questions_asked = len(context.session_history) if context.session_history else 0
        
        if questions_asked < 3:
            # Early stage - ask broad questions
            follow_ups = job_context.get("follow_up_questions", [])
            if follow_ups:
                return follow_ups[questions_asked % len(follow_ups)]
        
        # Later stage - dig deeper into specifics
        if "team" in user_input.lower() and "collaboration" not in str(context.session_history):
            return "That's interesting. Can you tell me more about how you collaborated with your team members?"
        elif "challenge" in user_input.lower() and "overcome" not in user_input.lower():
            return "What specific steps did you take to overcome that challenge?"
        elif any(metric in user_input.lower() for metric in ["increased", "decreased", "improved"]):
            return "Those are impressive results. How did you measure and track that impact?"
        else:
            # Generic follow-up
            scenarios = job_context.get("common_scenarios", [])
            if scenarios and questions_asked < len(scenarios):
                scenario = scenarios[questions_asked % len(scenarios)]
                return f"Let's move on. Tell me about a time when you were {scenario}."
            
        return "Thank you for sharing that. Is there anything else you'd like to add about that experience?"
    
    def _generate_feedback(self,
                          structure: Dict,
                          clarity: float,
                          specificity: float,
                          context: InterviewContext) -> Dict[str, str]:
        """Generate detailed feedback"""
        
        feedback = {}
        
        # Structure feedback
        if structure["overall"] >= 0.75:
            feedback["structure"] = "Excellent use of the STAR method. Your answer was well-organized."
        elif structure["overall"] >= 0.5:
            feedback["structure"] = "Good structure, but consider adding more details about the result/impact."
        else:
            feedback["structure"] = "Try to structure your answer using STAR: Situation, Task, Action, Result."
        
        # Content feedback
        if specificity >= 0.7:
            feedback["content"] = "Great job including specific examples and metrics!"
        elif specificity >= 0.4:
            feedback["content"] = "Good content, but try to include more specific numbers or examples."
        else:
            feedback["content"] = "Add more specific details, metrics, or examples to strengthen your answer."
        
        # Delivery feedback
        if clarity >= 0.8:
            feedback["delivery"] = "Clear and concise communication. Well done!"
        elif clarity >= 0.6:
            feedback["delivery"] = "Generally clear, but some sentences could be more concise."
        else:
            feedback["delivery"] = "Try to make your sentences shorter and more focused."
        
        # Relevance feedback
        job_key = context.job_title.lower().replace(" ", "-")
        job_skills = self.knowledge_base.get(job_key, {}).get("key_skills", [])
        
        last_response = ""
        if context.session_history and len(context.session_history) > 0:
            last_response = context.session_history[-1].get("user_response", "")
        
        skill_mentioned = any(skill in last_response.lower() for skill in job_skills)
        
        if skill_mentioned:
            feedback["relevance"] = f"Good job highlighting relevant skills for a {context.job_title} role."
        else:
            feedback["relevance"] = f"Consider emphasizing skills like {', '.join(job_skills[:2])} that are key for this role."
        
        return feedback
    
    def _get_improvements(self, 
                         structure: Dict, 
                         clarity: float, 
                         specificity: float) -> List[str]:
        """Generate specific improvement suggestions"""
        improvements = []
        # Check STAR components
        if "components" in structure:
            missing_components = [comp for comp, score in structure["components"].items() if score < 0.5]
            if missing_components:
                improvements.append(f"Include more details about the {', '.join(missing_components)}")
        if specificity < 0.5:
            improvements.append("Add specific metrics, numbers, or concrete examples")
            improvements.append("Mention the tools or technologies you used")
        if clarity < 0.7:
            improvements.append("Use shorter, more focused sentences")
            improvements.append("Avoid jargon unless necessary")
        if not improvements:
            improvements.append("Consider adding what you learned from this experience")
            improvements.append("Mention how this experience prepares you for the target role")
        return improvements[:3]  # Return top 3 improvements
    
    def _calculate_score(self, structure: float, clarity: float, specificity: float) -> float:
        """Calculate overall response score"""
        weights = {
            "structure": 0.4,
            "clarity": 0.3,
            "specificity": 0.3
        }
        
        score = (
            weights["structure"] * structure +
            weights["clarity"] * clarity +
            weights["specificity"] * specificity
        )
        
        return round(score, 2)