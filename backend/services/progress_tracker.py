from typing import Dict, List, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models.planner_models import InterviewPlan, ProgressLog, Achievement, UserAchievement

class ProgressTracker:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def calculate_plan_progress(self, plan: InterviewPlan) -> Dict[str, Any]:
        """计算计划进度"""
        progress = {
            "courses": {"completed": 0, "total": len(plan.recommended_courses or []), "percentage": 0},
            "projects": {"completed": 0, "total": len(plan.recommended_projects or []), "percentage": 0},
            "interviews": {"completed": plan.interviews_completed, "target": 5, "percentage": 0}
        }
        
        # 计算课程进度
        course_logs = self.db.query(ProgressLog).filter(
            ProgressLog.plan_id == plan.id,
            ProgressLog.activity_type == "course"
        ).all()
        
        completed_courses = sum(1 for log in course_logs if log.completed)
        progress["courses"]["completed"] = completed_courses
        progress["courses"]["percentage"] = (completed_courses / progress["courses"]["total"]) * 100 if progress["courses"]["total"] > 0 else 0
        
        # 计算项目进度
        project_logs = self.db.query(ProgressLog).filter(
            ProgressLog.plan_id == plan.id,
            ProgressLog.activity_type == "project"
        ).all()
        
        completed_projects = sum(1 for log in project_logs if log.completed)
        progress["projects"]["completed"] = completed_projects
        progress["projects"]["percentage"] = (completed_projects / progress["projects"]["total"]) * 100 if progress["projects"]["total"] > 0 else 0
        
        # 计算面试进度
        progress["interviews"]["percentage"] = (plan.interviews_completed / progress["interviews"]["target"]) * 100
        
        return progress
    
    def check_achievements(self, plan_id: str) -> List[str]:
        """检查是否获得新成就"""
        plan = self.db.query(InterviewPlan).filter(InterviewPlan.id == plan_id).first()
        if not plan:
            return []
        
        new_badges = []
        progress = self.calculate_plan_progress(plan)
        
        # 检查各种成就
        if progress["courses"]["percentage"] >= 100:
            new_badges.append("🎓 学习达人")
        
        if progress["projects"]["percentage"] >= 100:
            new_badges.append("💻 代码高手")
        
        if progress["interviews"]["completed"] >= 5:
            new_badges.append("🎤 面试专家")
        
        # 检查技能匹配度成就
        if plan.skill_match_score and plan.skill_match_score >= 90:
            new_badges.append("🎯 技能专家")
        
        # 检查经验匹配度成就
        if plan.experience_match_score and plan.experience_match_score >= 85:
            new_badges.append("⭐ 经验丰富")
        
        # 更新用户成就
        current_badges = plan.badges_earned or []
        for badge in new_badges:
            if badge not in current_badges:
                current_badges.append(badge)
        
        plan.badges_earned = current_badges
        self.db.commit()
        
        return new_badges
    
    def update_progress(
        self, 
        plan_id: str, 
        activity_type: str, 
        activity_id: str, 
        activity_name: str, 
        progress_percentage: float, 
        completed: bool = False
    ) -> Dict[str, Any]:
        """更新学习进度"""
        plan = self.db.query(InterviewPlan).filter(InterviewPlan.id == plan_id).first()
        if not plan:
            return {"success": False, "error": "Plan not found"}
        
        # 创建或更新进度日志
        progress_log = ProgressLog(
            plan_id=plan_id,
            activity_type=activity_type,
            activity_id=activity_id,
            activity_name=activity_name,
            progress_percentage=progress_percentage,
            completed=completed
        )
        
        if completed:
            progress_log.completed_at = datetime.utcnow()
        
        self.db.add(progress_log)
        self.db.commit()
        
        # 检查是否获得新成就
        new_badges = self.check_achievements(plan_id)
        
        return {
            "success": True,
            "new_badges": new_badges,
            "progress": self.calculate_plan_progress(plan)
        }
    
    def get_user_progress_summary(self, user_id: str) -> Dict[str, Any]:
        """获取用户进度总结"""
        plans = self.db.query(InterviewPlan).filter(InterviewPlan.user_id == user_id).all()
        
        total_plans = len(plans)
        completed_plans = sum(1 for plan in plans if plan.interviews_completed >= 5)
        total_badges = sum(len(plan.badges_earned or []) for plan in plans)
        
        return {
            "total_plans": total_plans,
            "completed_plans": completed_plans,
            "total_badges": total_badges,
            "completion_rate": (completed_plans / total_plans * 100) if total_plans > 0 else 0
        } 