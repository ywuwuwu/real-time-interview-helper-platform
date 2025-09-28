# app_memory.py — 基于内存存储的Interview Helper Backend
# =============================================================================
# 不使用数据库的简化版本，使用内存存储
# =============================================================================
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import io
from pathlib import Path
from dotenv import load_dotenv
import json
import uuid
from fastapi import WebSocket, WebSocketDisconnect
import urllib.parse

# FastAPI 路由
from fastapi import APIRouter
load_dotenv()

# 检查API Key
if not os.getenv("OPENAI_API_KEY"):
    print("[提示] 未检测到OPENAI_API_KEY，请将你的OpenAI API Key写入 backend/.env 文件，如 OPENAI_API_KEY=sk-xxx ...")

# Import our modules
from config import config
from rag.rag_pipeline import RAGPipeline, InterviewContext
from tts.voice_synthesis import stream_and_save_tts
from fastapi.responses import StreamingResponse
from services.real_ai_service import RealAIService

app = FastAPI(title="Interview Helper API (Memory Version)", version="1.0.0")

# 内存存储
interview_plans = {}  # 存储面试计划
progress_logs = {}    # 存储进度日志
achievements = {}     # 存储成就

# Initialize services
rag_pipeline = RAGPipeline()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(">>> This is the actual app_memory.py being loaded")
print(">>> Memory storage initialized")

# ===== Request/Response Models =====
class TranscribeResponse(BaseModel):
    text: str
    confidence: Optional[float] = None
    duration: Optional[float] = None

class RAGRequest(BaseModel):
    user_input: str
    job_title: Optional[str] = None
    job_desc: Optional[str] = None
    interview_type: Optional[str] = "behavioral"
    session_id: Optional[str] = None

class RAGResponse(BaseModel):
    ai_response: str
    feedback: Dict[str, str]
    suggested_improvements: List[str]
    score: Optional[float] = None

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "alloy"

class JobResponse(BaseModel):
    id: str
    title: str
    category: str
    description: Optional[str]
    skills: List[str]
    experience_level: Optional[str]

class SessionResponse(BaseModel):
    session_id: str
    job_title: str
    start_time: datetime
    questions_count: int
    overall_score: Optional[float] = None

# ===== Interview Planner Models =====
class InterviewPlanRequest(BaseModel):
    job_title: str
    job_description: str
    target_company: Optional[str] = None
    experience_years: Optional[int] = None
    skills: List[str] = []
    career_goals: Optional[str] = None

class InterviewPlanResponse(BaseModel):
    id: str
    job_title: str
    skill_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    gap_analysis: Dict[str, Any] = {}
    recommended_courses: List[Dict[str, Any]] = []
    recommended_projects: List[Dict[str, Any]] = []
    recommended_practice: List[Dict[str, Any]] = []
    progress: Dict[str, Any] = {}
    badges_earned: List[str] = []

class ProgressUpdateRequest(BaseModel):
    activity_type: str  # course, project, interview
    activity_id: str
    activity_name: str
    progress_percentage: float
    completed: bool = False

# ===== Memory-based Progress Tracker =====
class MemoryProgressTracker:
    def __init__(self):
        self.progress_data = {}
        
    def calculate_plan_progress(self, plan_id: str) -> Dict[str, Any]:
        """计算计划进度"""
        if plan_id not in self.progress_data:
            return {
                "courses_progress": 0,
                "projects_progress": 0,
                "interviews_completed": 0,
                "overall_progress": 0
            }
        
        progress = self.progress_data[plan_id]
        courses_progress = sum(progress.get("courses", {}).values()) / max(len(progress.get("courses", {})), 1)
        projects_progress = sum(progress.get("projects", {}).values()) / max(len(progress.get("projects", {})), 1)
        interviews_completed = progress.get("interviews", 0)
        
        overall_progress = (courses_progress + projects_progress + interviews_completed * 0.3) / 3
        
        return {
            "courses_progress": courses_progress,
            "projects_progress": projects_progress,
            "interviews_completed": interviews_completed,
            "overall_progress": min(overall_progress, 1.0)
        }
    
    def update_progress(
        self,
        plan_id: str,
        activity_type: str,
        activity_id: str,
        activity_name: str,
        progress_percentage: float,
        completed: bool = False
    ) -> Dict[str, Any]:
        """更新进度"""
        if plan_id not in self.progress_data:
            self.progress_data[plan_id] = {"courses": {}, "projects": {}, "interviews": 0}
        
        if activity_type == "course":
            self.progress_data[plan_id]["courses"][activity_id] = progress_percentage
        elif activity_type == "project":
            self.progress_data[plan_id]["projects"][activity_id] = progress_percentage
        elif activity_type == "interview":
            if completed:
                self.progress_data[plan_id]["interviews"] += 1
        
        return self.calculate_plan_progress(plan_id)

# Initialize services
real_ai_service = RealAIService(config.OPENAI_API_KEY)
progress_tracker = MemoryProgressTracker()

# ===== Mount ASR Transcribe Router =====
from asr.transcribe import router as transcribe_router
app.include_router(transcribe_router, prefix="/transcribe", tags=["ASR"])

# ===== Example Endpoints =====
@app.post("/api/rag", response_model=RAGResponse)
async def rag_endpoint(request: RAGRequest):
    """RAG问答端点"""
    try:
        # 创建面试上下文
        context = InterviewContext(
            job_title=request.job_title,
            job_description=request.job_desc,
            interview_type=request.interview_type
        )
        
        # 处理用户输入
        result = await rag_pipeline.process_user_input(
            user_input=request.user_input,
            context=context
        )
        
        return RAGResponse(
            ai_response=result["ai_response"],
            feedback=result["feedback"],
            suggested_improvements=result["suggested_improvements"],
            score=result.get("score")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """文本转语音"""
    try:
        audio_generator = stream_and_save_tts(request.text, request.voice)
        return StreamingResponse(
            audio_generator,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag-tts")
async def rag_tts_endpoint(request: RAGRequest):
    """RAG + TTS 组合端点"""
    try:
        # 1. RAG处理
        context = InterviewContext(
            job_title=request.job_title,
            job_description=request.job_desc,
            interview_type=request.interview_type
        )
        
        result = await rag_pipeline.process_user_input(
            user_input=request.user_input,
            context=context
        )
        
        # 2. TTS转换
        audio_generator = stream_and_save_tts(result["ai_response"], "alloy")
        
        return StreamingResponse(
            audio_generator,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=rag_tts.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-memory",
        "ai_service": "real_openai"
    }

# ===== Interview Planner Endpoints =====
@app.post("/api/planner/create", response_model=InterviewPlanResponse)
async def create_interview_plan(request: InterviewPlanRequest):
    """创建面试规划"""
    try:
        plan_id = str(uuid.uuid4())
        
        # 1. 保存用户画像和JD
        plan = {
            "id": plan_id,
            "job_title": request.job_title,
            "job_description": request.job_description,
            "target_company": request.target_company,
            "experience_years": request.experience_years,
            "skills": request.skills,
            "career_goals": request.career_goals,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 2. 调用真实AI分析匹配度
        analysis_result = await real_ai_service.analyze_job_match(
            request.job_description, 
            request.skills, 
            request.experience_years or 0
        )
        
        # 3. 生成真实AI推荐
        recommendations = await real_ai_service.generate_recommendations(analysis_result)
        
        # 4. 更新计划
        plan.update({
            "skill_match_score": analysis_result["skill_match"],
            "experience_match_score": analysis_result["experience_match"],
            "gap_analysis": analysis_result,
            "recommended_courses": recommendations["courses"],
            "recommended_projects": recommendations["projects"],
            "recommended_practice": recommendations["practice"],
            "badges_earned": []
        })
        
        # 5. 保存到内存
        interview_plans[plan_id] = plan
        
        # 6. 计算进度
        progress = progress_tracker.calculate_plan_progress(plan_id)
        
        return InterviewPlanResponse(
            id=plan["id"],
            job_title=plan["job_title"],
            skill_match_score=plan["skill_match_score"],
            experience_match_score=plan["experience_match_score"],
            gap_analysis=plan["gap_analysis"],
            recommended_courses=plan["recommended_courses"],
            recommended_projects=plan["recommended_projects"],
            recommended_practice=plan["recommended_practice"],
            progress=progress,
            badges_earned=plan["badges_earned"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/planner/{plan_id}", response_model=InterviewPlanResponse)
async def get_interview_plan(plan_id: str):
    """获取面试规划详情"""
    plan = interview_plans.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # 计算进度
    progress = progress_tracker.calculate_plan_progress(plan_id)
    
    return InterviewPlanResponse(
        id=plan["id"],
        job_title=plan["job_title"],
        skill_match_score=plan["skill_match_score"],
        experience_match_score=plan["experience_match_score"],
        gap_analysis=plan["gap_analysis"],
        recommended_courses=plan["recommended_courses"],
        recommended_projects=plan["recommended_projects"],
        recommended_practice=plan["recommended_practice"],
        progress=progress,
        badges_earned=plan["badges_earned"]
    )

@app.post("/api/planner/{plan_id}/progress")
async def update_progress(plan_id: str, request: ProgressUpdateRequest):
    """更新学习进度"""
    plan = interview_plans.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    result = progress_tracker.update_progress(
        plan_id=plan_id,
        activity_type=request.activity_type,
        activity_id=request.activity_id,
        activity_name=request.activity_name,
        progress_percentage=request.progress_percentage,
        completed=request.completed
    )
    
    return {
        "message": "Progress updated successfully",
        "progress": result
    }

@app.post("/api/planner/{plan_id}/upload-resume")
async def upload_resume(plan_id: str, file: UploadFile = File(...)):
    """上传简历文件"""
    plan = interview_plans.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    try:
        # 保存文件
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / f"resume_{plan_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 使用真实AI解析简历
        resume_content = await real_ai_service.parse_resume(str(file_path))
        
        # 更新计划
        plan["resume_path"] = str(file_path)
        plan["parsed_resume"] = resume_content
        plan["updated_at"] = datetime.now().isoformat()
        
        return {
            "message": "Resume uploaded and parsed successfully",
            "resume_data": resume_content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/planner/user/{user_id}/summary")
async def get_user_planner_summary(user_id: str):
    """获取用户规划总结"""
    user_plans = [plan for plan in interview_plans.values() if plan.get("user_id") == user_id]
    
    total_plans = len(user_plans)
    completed_plans = len([p for p in user_plans if p.get("status") == "completed"])
    avg_progress = sum(progress_tracker.calculate_plan_progress(p["id"])["overall_progress"] for p in user_plans) / max(total_plans, 1)
    
    return {
        "user_id": user_id,
        "total_plans": total_plans,
        "completed_plans": completed_plans,
        "average_progress": avg_progress,
        "recent_plans": user_plans[-5:] if user_plans else []
    }

# ===== WebSocket Router =====
ws_router = APIRouter()
print(">>> registering ws_router")
app.include_router(ws_router)
print(">>> ws_router included")

@ws_router.websocket("/ws/interview")
async def interview_ws(websocket: WebSocket):
    """面试WebSocket连接"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # 处理WebSocket消息
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("WebSocket disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 