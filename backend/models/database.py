# models/database.py — Version 1.1.1
# =============================================================================
# Interview Helper Backend — Database Models & ORM
#
# Overview:
#   - Defines SQLAlchemy ORM models for users, jobs, interview sessions, questions, and feedback templates.
#   - Handles database schema creation and initialization with default job and feedback data.
#   - Provides a Database utility class for session management and setup.
#
# Main Models:
#   1. User              — User accounts and interview history
#   2. Job               — Job positions, requirements, and evaluation criteria
#   3. InterviewSession  — Mock interview session metadata and scoring
#   4. Question          — Individual interview questions, user responses, and AI feedback
#   5. FeedbackTemplate  — Templates for structured feedback generation
#
# Usage:
#   - Instantiated and used in backend/app.py to initialize tables and provide DB sessions.
#   - Called at startup for table creation and default data population.
#   - Accessed throughout the backend for CRUD operations on users, jobs, sessions, and questions.
#
# Dependencies:
#   - SQLAlchemy         : ORM and schema management
#   - Python datetime    : Timestamps
#   - uuid               : Unique ID generation
#
# Author: BeeBee AI Track-B
# Version: 1.1.1
# =============================================================================

from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship("InterviewSession", back_populates="user")
    plans = relationship("InterviewPlan", back_populates="user")
    
class Job(Base):
    """Job position model"""
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False)
    description = Column(Text)
    skills = Column(JSON)  # List of required skills
    experience_level = Column(String)  # junior, mid, senior
    
    # Knowledge base
    common_questions = Column(JSON)  # List of common interview questions
    evaluation_criteria = Column(JSON)  # Criteria for scoring
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InterviewSession(Base):
    """Interview practice session"""
    __tablename__ = "interview_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Optional for anonymous users
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    
    # Session details
    interview_type = Column(String, default="behavioral")  # behavioral, technical, mixed
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Scores
    overall_score = Column(Float, nullable=True)
    structure_score = Column(Float, nullable=True)
    content_score = Column(Float, nullable=True)
    delivery_score = Column(Float, nullable=True)
    
    # Custom job description if uploaded
    custom_job_desc = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    job = relationship("Job")
    questions = relationship("Question", back_populates="session")

class Question(Base):
    """Individual question in a session"""
    __tablename__ = "questions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("interview_sessions.id"), nullable=False)
    
    # Question details
    question_text = Column(Text, nullable=False)
    question_type = Column(String)  # behavioral, technical, situational
    order_index = Column(Integer)  # Order in the session
    
    # User response
    user_response_text = Column(Text)
    user_response_audio_path = Column(String, nullable=True)  # Path to audio file
    response_duration_seconds = Column(Float, nullable=True)
    
    # AI feedback
    ai_feedback = Column(JSON)  # Structured feedback
    score = Column(Float, nullable=True)
    improvements = Column(JSON)  # List of suggested improvements
    
    # Timestamps
    asked_at = Column(DateTime, default=datetime.utcnow)
    answered_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="questions")

class FeedbackTemplate(Base):
    """Templates for generating feedback"""
    __tablename__ = "feedback_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    category = Column(String, nullable=False)  # structure, content, delivery, etc.
    condition = Column(String, nullable=False)  # good, average, poor
    template = Column(Text, nullable=False)
    min_score = Column(Float)
    max_score = Column(Float)

# Database setup
class Database:
    def __init__(self, database_url: str = "sqlite:///./interview_helper.db"):
        self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def init_default_data(self):
        """Initialize with default data"""
        session = self.get_session()
        
        # Check if already initialized
        if session.query(Job).count() > 0:
            session.close()
            return
        
        # Add default jobs
        default_jobs = [
            {
                "title": "Software Engineer",
                "category": "Engineering",
                "description": "Develop and maintain software applications",
                "skills": ["Python", "JavaScript", "SQL", "Git", "API Design"],
                "experience_level": "mid",
                "common_questions": [
                    "Tell me about a challenging bug you've fixed",
                    "How do you approach code reviews?",
                    "Describe your experience with system design",
                    "How do you ensure code quality?",
                    "Tell me about a time you had to learn a new technology quickly"
                ],
                "evaluation_criteria": {
                    "technical_depth": 0.3,
                    "problem_solving": 0.3,
                    "communication": 0.2,
                    "teamwork": 0.2
                }
            },
            {
                "title": "Data Scientist",
                "category": "Data & Analytics",
                "description": "Analyze data and build machine learning models",
                "skills": ["Python", "Machine Learning", "Statistics", "SQL", "Data Visualization"],
                "experience_level": "mid",
                "common_questions": [
                    "Walk me through a machine learning project you've worked on",
                    "How do you handle imbalanced datasets?",
                    "Explain a complex analysis to a non-technical stakeholder",
                    "How do you validate your models?",
                    "Tell me about a time your analysis influenced a business decision"
                ],
                "evaluation_criteria": {
                    "technical_knowledge": 0.35,
                    "analytical_thinking": 0.25,
                    "business_acumen": 0.2,
                    "communication": 0.2
                }
            },
            {
                "title": "Product Manager",
                "category": "Product",
                "description": "Lead product strategy and development",
                "skills": ["Product Strategy", "Data Analysis", "Stakeholder Management", "Agile", "User Research"],
                "experience_level": "senior",
                "common_questions": [
                    "How do you prioritize features?",
                    "Tell me about a product you launched",
                    "How do you measure product success?",
                    "Describe a time you had to say no to a stakeholder",
                    "How do you incorporate user feedback?"
                ],
                "evaluation_criteria": {
                    "strategic_thinking": 0.3,
                    "analytical_skills": 0.25,
                    "leadership": 0.25,
                    "communication": 0.2
                }
            },
            {
                "title": "公务员",
                "category": "Government",
                "description": "负责政府相关事务管理、政策执行与公共服务。",
                "skills": ["政策理解", "沟通能力", "应急处理", "组织协调", "法律法规"],
                "experience_level": "junior",
                "common_questions": [
                    "请你谈谈对当前社会热点问题的看法。",
                    "遇到群众上访情绪激动，你会如何处理？",
                    "如何看待公务员的服务意识？",
                    "如果你的上级让你做一件你认为不合理的事，你会怎么办？",
                    "谈谈你对政府信息公开的理解。"
                ],
                "evaluation_criteria": {
                    "政策理解": 0.3,
                    "沟通表达": 0.2,
                    "应变能力": 0.2,
                    "组织协调": 0.15,
                    "职业素养": 0.15
                }
            }
        ]
        
        for job_data in default_jobs:
            job = Job(**job_data)
            session.add(job)
        
        # Add feedback templates
        feedback_templates = [
            # Structure feedback
            {
                "category": "structure",
                "condition": "good",
                "template": "Excellent use of the STAR method. Your answer was well-organized and easy to follow.",
                "min_score": 0.8,
                "max_score": 1.0
            },
            {
                "category": "structure",
                "condition": "average",
                "template": "Good structure overall. Consider adding more details about the {missing_component}.",
                "min_score": 0.5,
                "max_score": 0.8
            },
            {
                "category": "structure",
                "condition": "poor",
                "template": "Try structuring your answer using STAR: Situation, Task, Action, and Result.",
                "min_score": 0.0,
                "max_score": 0.5
            },
            # Content feedback
            {
                "category": "content",
                "condition": "good",
                "template": "Great job including specific examples and quantifiable results!",
                "min_score": 0.8,
                "max_score": 1.0
            },
            {
                "category": "content",
                "condition": "average",
                "template": "Good content. Try to include more specific metrics or examples to strengthen your answer.",
                "min_score": 0.5,
                "max_score": 0.8
            },
            {
                "category": "content",
                "condition": "poor",
                "template": "Add more specific details and examples. Quantify your achievements when possible.",
                "min_score": 0.0,
                "max_score": 0.5
            }
        ]
        
        for template_data in feedback_templates:
            template = FeedbackTemplate(**template_data)
            session.add(template)
        
        session.commit()
        session.close()

# Usage example
# db = Database()
# db.create_tables()
# db.init_default_data()