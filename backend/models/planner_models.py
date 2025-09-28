from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base

class InterviewPlan(Base):
    """Interview planning session"""
    __tablename__ = "interview_plans"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Plan details
    job_title = Column(String, nullable=False)
    job_description = Column(Text, nullable=False)
    target_company = Column(String, nullable=True)
    
    # User profile
    resume_path = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    skills = Column(JSON)  # List of user skills
    career_goals = Column(Text, nullable=True)
    
    # Analysis results
    skill_match_score = Column(Float, nullable=True)
    experience_match_score = Column(Float, nullable=True)
    gap_analysis = Column(JSON)  # Detailed gap analysis
    
    # Recommendations
    recommended_courses = Column(JSON)
    recommended_projects = Column(JSON)
    recommended_practice = Column(JSON)
    
    # Progress tracking
    courses_progress = Column(JSON)  # {course_id: progress_percentage}
    projects_progress = Column(JSON)  # {project_id: progress_percentage}
    interviews_completed = Column(Integer, default=0)
    
    # Achievements
    badges_earned = Column(JSON)  # List of earned badges
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="plans")
    progress_logs = relationship("ProgressLog", back_populates="plan")

class ProgressLog(Base):
    """Progress tracking for plans"""
    __tablename__ = "progress_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id = Column(String, ForeignKey("interview_plans.id"), nullable=False)
    
    # Log details
    activity_type = Column(String, nullable=False)  # course, project, interview
    activity_id = Column(String, nullable=False)
    activity_name = Column(String, nullable=False)
    progress_percentage = Column(Float, default=0.0)
    completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    plan = relationship("InterviewPlan", back_populates="progress_logs")

class Achievement(Base):
    """Achievement badges system"""
    __tablename__ = "achievements"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=False)  # Emoji or icon
    criteria = Column(JSON)  # Achievement criteria
    points = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

class UserAchievement(Base):
    """User achievement tracking"""
    __tablename__ = "user_achievements"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(String, ForeignKey("achievements.id"), nullable=False)
    plan_id = Column(String, ForeignKey("interview_plans.id"), nullable=True)
    
    # Achievement details
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    achievement = relationship("Achievement")
    plan = relationship("InterviewPlan") 