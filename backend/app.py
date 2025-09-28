# app.py — Version 1.1.1 
# =============================================================================
# Interview Helper Backend (app.py)
#
# Overview:
#   - FastAPI-based backend service for AI-powered mock interview practice.
#   - Provides RESTful APIs for job management, interview session workflows, AI Q&A (RAG), 
#     job description upload/advice, statistics, and health checks.
#   - Integrates with OpenAI for LLM-based question/feedback generation and Whisper for ASR.
#
# Key Endpoints:
#   1. POST   /api/rag               — Process interview dialog, generate AI questions, feedback, and suggestions
#   2. POST   /api/sessions/start    — Start a new interview session and auto-generate the first question
#   3. GET    /api/sessions/{id}     — Retrieve all questions, answers, and feedback for a session
#   4. POST   /api/sessions/{id}/end — End a session and calculate scores
#   5. GET    /api/jobs              — List available job positions
#   6. GET    /api/jobs/{id}         — Get details for a specific job
#   7. POST   /api/upload-job-desc   — Upload and parse a job description file
#   8. POST   /api/jd_advice         — Generate preparation advice based on a job description
#   9. POST   /transcribe            — Speech-to-text (ASR) endpoint (OpenAI Whisper)
#  10. GET    /api/stats             — Retrieve user interview statistics
#  11. GET    /api/health            — Health check
#
# Dependencies:
#   - FastAPI / Uvicorn       : Web framework and server
#   - SQLAlchemy              : Database ORM
#   - OpenAI API              : LLM Q&A and ASR
#   - python-dotenv           : Environment variable management
#
# Author: BeeBee AI Track-B
# Version: 1.1.1
# =============================================================================
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import io
from pathlib import Path
from dotenv import load_dotenv
import json
import uuid
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import urllib.parse


# FastAPI 路由
from fastapi import APIRouter
load_dotenv()

# 检查API Key
if not os.getenv("OPENAI_API_KEY"):
    print("[提示] 未检测到OPENAI_API_KEY，请将你的OpenAI API Key写入 backend/.env 文件，如 OPENAI_API_KEY=sk-xxx ...")

# Import our modules
from config import config
from models.database import Database, User, Job, InterviewSession, Question
from models.planner_models import InterviewPlan, ProgressLog, Achievement, UserAchievement
# from asr.transcription import CachedTranscriptionService  # 已移除
from rag.rag_pipeline import RAGPipeline, InterviewContext
from tts.voice_synthesis import stream_and_save_tts
from fastapi.responses import StreamingResponse
from services.planner_analysis import PlannerAnalysisService
from services.progress_tracker import ProgressTracker

# from asr.transcription import router as asr_router  # 已移除
# app.include_router(asr_router, prefix="/api/transcribe")  # 已移除
app = FastAPI(title="Interview Helper API", version="1.0.0")

# Initialize services
db = Database(config.DATABASE_URL)
# db.create_tables()
# db.init_default_data()
@app.on_event("startup")
def startup_event():
    db.create_tables()
    db.init_default_data()
    print(">>> Database tables created & default data initialized")
# transcription_service = CachedTranscriptionService(backend="mock")  # 已移除
# transcription_service = CachedTranscriptionService(
#     backend=config.DEFAULT_ASR_BACKEND, 
#     use_cache=True
# )
rag_pipeline = RAGPipeline()
# tts_service = TTSService(provider="mock")
planner_analysis = PlannerAnalysisService(config.OPENAI_API_KEY)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print(">>> This is the actual app.py being loaded")
# ===== Example Models =====
# ===== Dependency =====
def get_db():
    """Database dependency"""
    db_session = db.get_session()
    try:
        yield db_session
    finally:
        db_session.close()

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
    # speed: Optional[float] = 1.0

class JobResponse(BaseModel):
    id: str
    title: str
    category: str
    description: Optional[str]
    skills: List[str]
    experience_level: Optional[str]

# ===== Mount ASR Transcribe Router =====
from asr.transcribe import router as transcribe_router
app.include_router(transcribe_router, prefix="/transcribe", tags=["ASR"])

# ===== Example Endpoints =====

# Removed old /transcribe endpoint to avoid conflict
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
    experience_years: Optional[int] = None
    skills: List[str] = []
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

# ===== Endpoints =====

@app.post("/api/rag", response_model=RAGResponse)
async def rag_endpoint(
    request: RAGRequest,
    db_session: Session = Depends(get_db)
):
    """Process user input through RAG pipeline"""
    try:
        # Get session if provided
        session = None
        if request.session_id:
            session = db_session.query(InterviewSession).filter_by(
                id=request.session_id
            ).first()
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        # Create context，优先用传入的job_desc
        context = InterviewContext(
            job_title=request.job_title or (session.job.title if session else ""),
            job_description=request.job_desc if request.job_desc else (session.job.description if session and session.job else None),
            interview_type=request.interview_type or "behavioral",
            session_history=[]
        )
        # If session exists, load history
        if session:
            questions = db_session.query(Question).filter_by(
                session_id=session.id
            ).order_by(Question.order_index).all()
            context.session_history = [
                {
                    "question": q.question_text,
                    "user_response": q.user_response_text,
                    "timestamp": q.asked_at.isoformat()
                }
                for q in questions
            ]
        # Generate response
        ai_response, analysis = rag_pipeline.generate_response(
            request.user_input, 
            context
        )
        # Save to database if session exists
        if session:
            question = Question(
                session_id=session.id,
                question_text=ai_response,
                user_response_text=request.user_input,
                order_index=len(context.session_history or []),
                ai_feedback=analysis["feedback"],
                score=analysis["score"],
                improvements=analysis["suggested_improvements"],
                answered_at=datetime.utcnow()
            )
            db_session.add(question)
            db_session.commit()
        return RAGResponse(
            ai_response=ai_response,
            feedback=analysis["feedback"],
            suggested_improvements=analysis["suggested_improvements"],
            score=analysis["score"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG processing failed: {str(e)}")

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech and stream to frontend while saving to file"""
    try:
        save_path = f"speech_{request.voice or 'alloy'}.mp3"
        return StreamingResponse(
            stream_and_save_tts(
                text=request.text,
                voice=request.voice or "alloy",
                # speed=request.speed or 1.0,
                save_path=save_path
            ),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename={save_path}"
            }
        )
    except ValueError as e:
        print("TTS ValueError:", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("TTS Exception:", e)
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

@app.post("/api/rag-tts")
async def rag_tts_endpoint(
    request: RAGRequest,
    db_session: Session = Depends(get_db)
):
    """
    RAG pipeline + TTS: returns both text and streamed audio of AI response
    """
    try:
        # 1. 调用原有 RAG pipeline 获取 AI 回复
        # (以下代码复用你的rag_endpoint逻辑)
        session = None
        if request.session_id:
            session = db_session.query(InterviewSession).filter_by(
                id=request.session_id
            ).first()
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        context = InterviewContext(
            job_title=request.job_title or (session.job.title if session else ""),
            job_description=request.job_desc if request.job_desc else (session.job.description if session and session.job else None),
            interview_type=request.interview_type or "behavioral",
            session_history=[]
        )
        if session:
            questions = db_session.query(Question).filter_by(
                session_id=session.id
            ).order_by(Question.order_index).all()
            context.session_history = [
                {
                    "question": q.question_text,
                    "user_response": q.user_response_text,
                    "timestamp": q.asked_at.isoformat()
                }
                for q in questions
            ]
        ai_response, analysis = rag_pipeline.generate_response(
            request.user_input, 
            context
        )
        if session:
            question = Question(
                session_id=session.id,
                question_text=ai_response,
                user_response_text=request.user_input,
                order_index=len(context.session_history or []),
                ai_feedback=analysis["feedback"],
                score=analysis["score"],
                improvements=analysis["suggested_improvements"],
                answered_at=datetime.utcnow()
            )
            db_session.add(question)
            db_session.commit()


        #  3. TTS合成与StreamingResponse返回
        voice = getattr(request, "voice", "alloy")
        model = getattr(request, "tts_model", "tts-1")
        save_path = f"speech_rag_{voice}.mp3"

        headers = {
            "X-RAG-Text": urllib.parse.quote(ai_response or ""),
            "X-RAG-Feedback": urllib.parse.quote(json.dumps(analysis.get("feedback", {}), ensure_ascii=False)),
            "X-RAG-Improvements": urllib.parse.quote(json.dumps(analysis.get("suggested_improvements", []), ensure_ascii=False)),
        }
        # 注意：stream_and_save_tts需返回生成器
        return StreamingResponse(
            stream_and_save_tts(ai_response, voice, model, save_path),
            media_type="audio/mpeg",
            headers=headers

            # headers={
            #     "X-RAG-Text": urllib.parse.quote(ai_response)  # 可自定义头返回原文
            # }
        )
    except Exception as e:
        print("RAG+TTS Exception:", e)
        raise HTTPException(status_code=500, detail=f"RAG+TTS failed: {str(e)}")

def multipart_rag_tts_generator(ai_response, analysis, audio_generator, boundary):
    # 1. JSON结构化文本部分
    json_part = (
        f"--{boundary}\r\n"
        "Content-Type: application/json\r\n\r\n"
        f"{json.dumps({'ai_response': ai_response, **analysis})}\r\n"
    )
    yield json_part.encode("utf-8")
    # 2. 音频部分
    audio_header = (
        f"--{boundary}\r\n"
        "Content-Type: audio/mpeg\r\n"
        'Content-Disposition: attachment; filename="speech.mp3"\r\n\r\n'
    )
    yield audio_header.encode("utf-8")
    for chunk in audio_generator:     # 用同步for循环
        yield chunk
    # 3. 结束标志
    yield f"\r\n--{boundary}--\r\n".encode("utf-8")
@app.post("/api/rag-tts-multipart")
async def rag_tts_multipart_endpoint(
    request: RAGRequest,
    db_session: Session = Depends(get_db)
):
    try:
        # --- 1. session与context加载 ---
        session = None
        if request.session_id:
            session = db_session.query(InterviewSession).filter_by(
                id=request.session_id
            ).first()
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        context = InterviewContext(
            job_title=request.job_title or (session.job.title if session else ""),
            job_description=request.job_desc if request.job_desc else (session.job.description if session and session.job else None),
            interview_type=request.interview_type or "behavioral",
            session_history=[]
        )
        if session:
            questions = db_session.query(Question).filter_by(
                session_id=session.id
            ).order_by(Question.order_index).all()
            context.session_history = [
                {
                    "question": q.question_text,
                    "user_response": q.user_response_text,
                    "timestamp": q.asked_at.isoformat()
                }
                for q in questions
            ]
        # --- 2. RAG pipeline生成反馈 ---
        ai_response, analysis = rag_pipeline.generate_response(
            request.user_input, 
            context
        )
        # --- 3. 数据库写入 ---
        if session:
            question = Question(
                session_id=session.id,
                question_text=ai_response,
                user_response_text=request.user_input,
                order_index=len(context.session_history or []),
                ai_feedback=analysis["feedback"],
                score=analysis["score"],
                improvements=analysis["suggested_improvements"],
                answered_at=datetime.utcnow()
            )
            db_session.add(question)
            db_session.commit()

        # --- 4. TTS音频流/multipart返回 ---
        voice = getattr(request, "voice", "alloy")
        model = getattr(request,  "tts-1")
        save_path = f"speech_rag_{voice}.mp3"
        audio_generator = stream_and_save_tts(ai_response, voice, model, save_path)
        boundary = f"BOUNDARY-{uuid.uuid4()}"  # 只生成一次！

        return StreamingResponse(
            multipart_rag_tts_generator(ai_response, analysis, audio_generator, boundary),
            media_type=f"multipart/x-mixed-replace; boundary={boundary}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG+TTS multipart failed: {str(e)}")

async def rag_tts_ws_handler(
    websocket: WebSocket,
    db_session: Session = Depends(get_db)
):
    print(">>> [WebSocket] rag_tts_ws_handler called")
    await websocket.accept()
    print(">>> Client connected")
    session_id = None
    context = None
    session = None

    try:
        while True:
            print(">>> Waiting for message...")
            data = await websocket.receive_json()
            print(">>> Received message:", data)
            user_input = data.get("user_input")
            job_title = data.get("job_title")
            job_desc = data.get("job_desc")
            interview_type = data.get("interview_type", "behavioral")
            voice = data.get("voice", "alloy")
            tts_model = data.get("tts_model", "tts-1")
            # 新会话逻辑
            if not session_id and "session_id" in data:
                session_id = data["session_id"]
                session = db_session.query(InterviewSession).filter_by(
                    id=session_id
                ).first()
            # 构建面试上下文
            context = InterviewContext(
                job_title=job_title or (session.job.title if session and session.job else ""),
                job_description=job_desc or (session.job.description if session and session.job else ""),
                interview_type=interview_type,
                session_history=[]
            )
            if session:
                questions = db_session.query(Question).filter_by(
                    session_id=session.id
                ).order_by(Question.order_index).all()
                context.session_history = [
                    {
                        "question": q.question_text,
                        "user_response": q.user_response_text,
                        "timestamp": q.asked_at.isoformat()
                    }
                    for q in questions
                ]
            # 1. RAG生成AI回复和结构化分析
            ai_response, analysis = rag_pipeline.generate_response(user_input, context)
            # 2. 写入数据库
            if session:
                question = Question(
                    session_id=session.id,
                    question_text=ai_response,
                    user_response_text=user_input,
                    order_index=len(context.session_history or []),
                    ai_feedback=analysis["feedback"],
                    score=analysis["score"],
                    improvements=analysis["suggested_improvements"],
                    answered_at=datetime.utcnow()
                )
                db_session.add(question)
                db_session.commit()
            # 3. 推送结构化文本反馈
            await websocket.send_json({
                "ai_response": ai_response,
                "feedback": analysis["feedback"],
                "suggested_improvements": analysis["suggested_improvements"],
                "score": analysis["score"]
            })
            # 4. 实时推送TTS音频chunk
            audio_gen = stream_and_save_tts(ai_response, voice, tts_model)
            for chunk in audio_gen:
                await websocket.send_bytes(chunk)
    # except WebSocketDisconnect:
    #     print("WebSocket closed.")
    except WebSocketDisconnect:
        print("WebSocket disconnected normally.")
    except Exception as e:
        print(f"WebSocket error: {e}")


print(">>> registering ws_router")
ws_router = APIRouter()
@ws_router.websocket("/ws/interview")
async def interview_ws(websocket: WebSocket, db_session: Session = Depends(get_db)):
    print("DEBUG: interview_ws")
    try:
        await rag_tts_ws_handler(websocket, db_session)
    except WebSocketDisconnect:
        print("WebSocket disconnected normally.")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
app.include_router(ws_router, tags=["WebSocket"])
print(">>> ws_router included")

@app.get("/api/jobs", response_model=List[JobResponse])
async def list_jobs(
    category: Optional[str] = None,
    db_session: Session = Depends(get_db)
):
    """Get available job positions"""
    query = db_session.query(Job)
    if category:
        query = query.filter(Job.category == category)
    jobs = query.all()
    return [
        JobResponse(
            id=str(job.id),
            title=str(job.title),
            category=str(job.category),
            description=str(job.description) if job.description is not None else None,
            skills=job.skills if isinstance(job.skills, list) else [],
            experience_level=str(job.experience_level) if job.experience_level is not None else None
        )
        for job in jobs
    ]

@app.get("/api/jobs/{job_id}")
async def get_job_details(
    job_id: str,
    db_session: Session = Depends(get_db)
):
    """Get details for a specific job"""
    job = db_session.query(Job).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "title": job.title,
        "category": job.category,
        "description": job.description,
        "skills": job.skills,
        "experience_level": job.experience_level,
        "common_questions": job.common_questions,
        "evaluation_criteria": job.evaluation_criteria
    }

@app.post("/api/sessions/start", response_model=SessionResponse)
async def start_session(
    job_id: str = Form(...),
    user_id: Optional[str] = Form(None),
    interview_type: str = Form("behavioral"),
    db_session: Session = Depends(get_db)
):
    """Start a new interview session"""
    # Verify job exists
    job = db_session.query(Job).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # Create session
    session = InterviewSession(
        user_id=user_id,
        job_id=job_id,
        interview_type=interview_type
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    # Ask first question
    first_question = Question(
        session_id=session.id,
        question_text="Tell me about yourself and why you're interested in this position.",
        question_type="behavioral",
        order_index=0
    )
    db_session.add(first_question)
    db_session.commit()
    return SessionResponse(
        session_id=str(session.id),
        job_title=str(job.title),
        start_time=session.start_time if isinstance(session.start_time, datetime) else datetime.utcnow(),
        questions_count=1
    )

@app.get("/api/sessions/{session_id}")
async def get_session(
    session_id: str,
    db_session: Session = Depends(get_db)
):
    """Get session details with all questions and feedback"""
    session = db_session.query(InterviewSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    questions = db_session.query(Question).filter_by(
        session_id=session_id
    ).order_by(Question.order_index).all()
    return {
        "session_id": session.id,
        "job": {
            "title": session.job.title,
            "category": session.job.category
        },
        "interview_type": session.interview_type,
        "start_time": session.start_time,
        "end_time": session.end_time,
        "duration_seconds": session.duration_seconds,
        "overall_score": session.overall_score,
        "questions": [
            {
                "id": q.id,
                "question": q.question_text,
                "user_response": q.user_response_text,
                "score": q.score,
                "feedback": q.ai_feedback,
                "improvements": q.improvements,
                "asked_at": q.asked_at,
                "answered_at": q.answered_at
            }
            for q in questions
        ]
    }

@app.post("/api/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    db_session: Session = Depends(get_db)
):
    """End interview session and calculate final scores"""
    session = db_session.query(InterviewSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    # Calculate scores
    questions = db_session.query(Question).filter_by(session_id=session_id).all()
    if questions:
        scores = [q.score for q in questions if q.score is not None]
        if scores:
            avg_score = sum(scores) / len(scores)
            db_session.query(InterviewSession).filter_by(id=session_id).update({"overall_score": avg_score})
    # Update session end_time and duration_seconds
    end_time = datetime.utcnow()
    duration = 0
    if isinstance(session.start_time, datetime):
        duration = int((end_time - session.start_time).total_seconds())
    db_session.query(InterviewSession).filter_by(id=session_id).update({"end_time": end_time, "duration_seconds": duration})
    db_session.commit()
    return {
        "session_id": session.id,
        "overall_score": session.overall_score,
        "duration_seconds": session.duration_seconds,
        "questions_asked": len(questions),
        "end_time": session.end_time
    }

@app.post("/api/upload-job-desc")
async def upload_job_description(
    file: UploadFile = File(...),
    job_title: Optional[str] = Form(None),
    db_session: Session = Depends(get_db)
):
    """Upload and parse job description"""
    try:
        # Validate file
        if file.content_type not in ["text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        content = await file.read()
        # Save file
        upload_dir = Path(config.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / f"{datetime.utcnow().timestamp()}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        # Extract text (simplified - in production use proper parsers)
        if file.content_type == "text/plain":
            text_content = content.decode("utf-8")
        else:
            # For PDF/DOCX, you'd use appropriate libraries
            text_content = "Parsed job description content"
        # Extract key information (mock implementation)
        extracted_info = {
            "title": job_title or "Extracted Job Title",
            "requirements": ["Requirement 1", "Requirement 2"],
            "skills": ["Python", "Communication", "Problem Solving"],
            "experience": "3-5 years"
        }
        return {
            "message": "Job description uploaded successfully",
            "file_path": str(file_path),
            "extracted_info": extracted_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/jd_advice")
async def jd_advice(
    jd_text: str = Form(None),
    file: UploadFile = File(None)
):
    try:
        print("DEBUG: 收到 jd_text =", jd_text)
        print("DEBUG: 收到 file =", file.filename if file else None)
        jd_content = None
        if jd_text and jd_text.strip():
            jd_content = jd_text.strip()
        elif file is not None:
            content = await file.read()
            try:
                jd_content = content.decode("utf-8")
            except Exception:
                jd_content = content.decode("latin1", errors="ignore")
        else:
            print("DEBUG: 没有收到JD文本或文件")
            raise HTTPException(status_code=400, detail="请提供JD文本或文件")
        print("DEBUG: jd_content =", jd_content[:100] if jd_content else None)
        context = InterviewContext(
            job_title="",
            job_description=jd_content,
            interview_type="behavioral",
            session_history=[]
        )
        user_input = (
    "请你作为一名AI面试教练，仔细阅读下面的岗位描述，并针对该岗位给出详细的面试准备建议，"
    "包括：1. 需要重点准备的知识和技能；2. 可能被问到的典型问题；3. 如何突出自己的优势；"
    "4. 其他有助于面试成功的建议。\n\n岗位描述：\n" + jd_content
)
        advice = rag_pipeline.generate_gpt_advice(user_input)
        return {"advice": advice}
        # print("DEBUG: advice =", advice)
        # return {"advice": advice}
    except Exception as e:
        print("JD_ADVICE ERROR:", e)
        raise HTTPException(status_code=500, detail=f"生成建议失败: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "rag": "ready",
            "tts": "ready"
        }
    }

@app.get("/api/stats")
async def get_statistics(
    user_id: Optional[str] = None,
    db_session: Session = Depends(get_db)
):
    """Get user statistics"""
    query = db_session.query(InterviewSession)
    if user_id:
        query = query.filter_by(user_id=user_id)
    sessions = query.all()
    if not sessions:
        return {
            "total_sessions": 0,
            "average_score": 0,
            "total_practice_time": 0,
            "most_practiced_role": None
        }
    # Calculate statistics
    total_time = sum(s.duration_seconds or 0 for s in sessions)
    scores = [float(s.overall_score) for s in sessions if s.overall_score is not None and isinstance(s.overall_score, (float, int))]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    # Most practiced role
    job_counts = {}
    for s in sessions:
        job_title = s.job.title
        job_counts[job_title] = job_counts.get(job_title, 0) + 1
    most_practiced = max(job_counts.items(), key=lambda x: x[1])[0] if job_counts else None
    return {
        "total_sessions": len(sessions),
        "average_score": round(avg_score, 2),
        "total_practice_time": total_time,
        "most_practiced_role": most_practiced,
        "recent_sessions": [
            {
                "id": s.id,
                "job_title": s.job.title,
                "date": s.start_time,
                "score": s.overall_score,
                "duration": s.duration_seconds
            }
            for s in sorted(sessions, key=lambda x: x.start_time if isinstance(x.start_time, datetime) else datetime.min, reverse=True)[:5]
        ]
    }

# ===== Interview Planner Endpoints =====

@app.post("/api/planner/create", response_model=InterviewPlanResponse)
async def create_interview_plan(
    request: InterviewPlanRequest,
    db_session: Session = Depends(get_db)
):
    """创建面试规划"""
    print(f"🚀 开始创建面试规划: {request.job_title}")
    print(f"📝 JD长度: {len(request.job_description)} 字符")
    print(f"👤 用户技能: {request.skills}")
    print(f"⏰ 工作经验: {request.experience_years} 年")
    
    try:
        # 1. 保存用户画像和JD
        plan = InterviewPlan(
            job_title=request.job_title,
            job_description=request.job_description,
            target_company=request.target_company,
            experience_years=request.experience_years,
            skills=request.skills,
            career_goals=request.career_goals
        )
        db_session.add(plan)
        db_session.commit()
        print(f"✅ 计划创建成功: {plan.id}")
        
        # 2. 调用AI分析匹配度
        print("🎯 开始AI分析匹配度...")
        analysis_result = await planner_analysis.analyze_job_match(
            request.job_description, 
            request.skills, 
            request.experience_years or 0
        )
        
        print(f"📊 AI分析结果:")
        print(f"  - 技能匹配度: {analysis_result['skill_match']}%")
        print(f"  - 经验匹配度: {analysis_result['experience_match']}%")
        print(f"  - 整体匹配度: {analysis_result['overall_match']}%")
        print(f"  - 差距数量: {len(analysis_result['gaps'])}")
        print(f"  - 优势数量: {len(analysis_result['strengths'])}")
        
        # 显示差距详情
        if analysis_result['gaps']:
            print("📋 技能差距详情:")
            for gap in analysis_result['gaps']:
                print(f"  - {gap['skill']} ({gap['status']}, 优先级: {gap['priority']})")
        
        # 显示优势详情
        if analysis_result['strengths']:
            print("✅ 技能优势详情:")
            for strength in analysis_result['strengths']:
                print(f"  - {strength['skill']} (重要性: {strength['importance']})")
        
        # 3. 生成推荐
        print("💡 开始生成推荐...")
        recommendations = await planner_analysis.generate_recommendations(analysis_result)
        
        print(f"📚 推荐生成完成:")
        print(f"  - 课程数量: {len(recommendations.get('courses', []))}")
        print(f"  - 项目数量: {len(recommendations.get('projects', []))}")
        print(f"  - 练习数量: {len(recommendations.get('practice', []))}")
        
        # 4. 更新计划
        plan.skill_match_score = analysis_result["skill_match"]
        plan.experience_match_score = analysis_result["experience_match"]
        plan.gap_analysis = analysis_result
        plan.recommended_courses = recommendations["courses"]
        plan.recommended_projects = recommendations["projects"]
        plan.recommended_practice = recommendations["practice"]
        
        db_session.commit()
        print(f"✅ 计划更新完成")
        
        # 5. 计算进度
        progress_tracker = ProgressTracker(db_session)
        progress = progress_tracker.calculate_plan_progress(plan)
        
        return InterviewPlanResponse(
            id=plan.id,
            job_title=plan.job_title,
            skill_match_score=plan.skill_match_score,
            experience_match_score=plan.experience_match_score,
            experience_years=plan.experience_years,
            skills=plan.skills,
            gap_analysis=plan.gap_analysis,
            recommended_courses=plan.recommended_courses,
            recommended_projects=plan.recommended_projects,
            recommended_practice=plan.recommended_practice,
            progress=progress,
            badges_earned=plan.badges_earned or []
        )
        
    except Exception as e:
        print(f"❌ 创建面试规划失败: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/planner/{plan_id}", response_model=InterviewPlanResponse)
async def get_interview_plan(
    plan_id: str,
    db_session: Session = Depends(get_db)
):
    """获取面试规划详情"""
    plan = db_session.query(InterviewPlan).filter(InterviewPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # 计算进度
    progress_tracker = ProgressTracker(db_session)
    progress = progress_tracker.calculate_plan_progress(plan)
    
    return InterviewPlanResponse(
        id=plan.id,
        job_title=plan.job_title,
        skill_match_score=plan.skill_match_score,
        experience_match_score=plan.experience_match_score,
        experience_years=plan.experience_years,
        skills=plan.skills,
        gap_analysis=plan.gap_analysis,
        recommended_courses=plan.recommended_courses,
        recommended_projects=plan.recommended_projects,
        recommended_practice=plan.recommended_practice,
        progress=progress,
        badges_earned=plan.badges_earned or []
    )

@app.post("/api/planner/{plan_id}/progress")
async def update_progress(
    plan_id: str,
    request: ProgressUpdateRequest,
    db_session: Session = Depends(get_db)
):
    """更新学习进度"""
    plan = db_session.query(InterviewPlan).filter(InterviewPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    progress_tracker = ProgressTracker(db_session)
    result = progress_tracker.update_progress(
        plan_id=plan_id,
        activity_type=request.activity_type,
        activity_id=request.activity_id,
        activity_name=request.activity_name,
        progress_percentage=request.progress_percentage,
        completed=request.completed
    )
    
    return result

@app.post("/api/planner/{plan_id}/upload-resume")
async def upload_resume(
    plan_id: str,
    file: UploadFile = File(...),
    db_session: Session = Depends(get_db)
):
    """上传简历"""
    print(f"📄 开始处理简历上传: plan_id={plan_id}, filename={file.filename}")
    
    plan = db_session.query(InterviewPlan).filter(InterviewPlan.id == plan_id).first()
    if not plan:
        print(f"❌ Plan not found: {plan_id}")
        raise HTTPException(status_code=404, detail="Plan not found")
    
    try:
        # 保存文件
        file_path = f"uploads/resumes/{plan_id}_{file.filename}"
        os.makedirs("uploads/resumes", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"✅ 简历文件保存成功: {file_path}")
        
        plan.resume_path = file_path
        
        # 解析简历内容
        print("🔍 开始解析简历内容...")
        try:
            resume_content = await planner_analysis.parse_resume(file_path)
            print(f"✅ 简历解析完成: {resume_content}")
            
            # 更新用户画像
            plan.skills = resume_content.get("skills", [])
            plan.experience_years = resume_content.get("experience_years")
            
            # 重新计算匹配度
            print("🎯 重新计算匹配度...")
            analysis_result = await planner_analysis.analyze_job_match(
                plan.job_description, 
                plan.skills, 
                plan.experience_years or 0
            )
            
            print(f"📊 匹配度计算结果:")
            print(f"  - 技能匹配度: {analysis_result['skill_match']}%")
            print(f"  - 经验匹配度: {analysis_result['experience_match']}%")
            print(f"  - 整体匹配度: {analysis_result['overall_match']}%")
            print(f"  - 差距数量: {len(analysis_result['gaps'])}")
            print(f"  - 优势数量: {len(analysis_result['strengths'])}")
            
            # 详细技能分析日志
            print(f"\n🔍 详细技能分析:")
            print(f"  - 用户技能总数: {len(plan.skills)}")
            print(f"  - 匹配技能: {len(analysis_result.get('strengths', []))} 项")
            print(f"  - 缺失技能: {len(analysis_result.get('gaps', []))} 项")
            
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
            user_skills = set(skill.lower() for skill in plan.skills)
            matched_skills = set(strength['skill'].lower() for strength in analysis_result.get('strengths', []))
            gap_skills = set(gap['skill'].lower() for gap in analysis_result.get('gaps', []))
            extra_skills = user_skills - matched_skills - gap_skills
            
            if extra_skills:
                print(f"\n💡 岗位没有要求的技能:")
                for skill in extra_skills:
                    print(f"    - {skill}")
            
            print(f"\n📋 技能匹配总结:")
            print(f"  - 匹配率: {len(analysis_result.get('strengths', []))}/{len(plan.skills)} = {analysis_result['skill_match']:.1f}%")
            print(f"  - 优势技能: {len(analysis_result.get('strengths', []))} 项")
            print(f"  - 需要提升: {len(analysis_result.get('gaps', []))} 项")
            print(f"  - 额外技能: {len(extra_skills)} 项")
            
            # 更新计划
            plan.skill_match_score = analysis_result["skill_match"]
            plan.experience_match_score = analysis_result["experience_match"]
            plan.gap_analysis = analysis_result
            
            db_session.commit()
            print(f"✅ 数据库更新完成")
            
            return {
                "success": True, 
                "resume_parsed": resume_content,
                "analysis_result": analysis_result,
                "message": "简历解析成功"
            }
            
        except ValueError as e:
            # 简历解析失败，返回明确的错误信息
            error_msg = str(e)
            print(f"❌ 简历解析失败: {error_msg}")
            
            # 清理已保存的文件
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ 已清理失败的文件: {file_path}")
            
            # 返回详细的错误信息和建议
            return {
                "success": False,
                "error": error_msg,
                "suggestions": [
                    "确保PDF文件没有损坏",
                    "尝试将PDF转换为文本文件",
                    "检查文件编码格式",
                    "确保PyPDF2库已正确安装: pip install PyPDF2==3.0.1",
                    "检查PDF文件是否包含文本内容",
                    "尝试使用其他PDF阅读器打开文件"
                ],
                "message": "简历解析失败，请检查文件格式或尝试其他方法"
            }
        
    except Exception as e:
        print(f"❌ 简历上传处理失败: {e}")
        # 清理已保存的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ 已清理失败的文件: {file_path}")
        
        raise HTTPException(
            status_code=500, 
            detail=f"简历上传失败: {str(e)}"
        )

@app.get("/api/planner/user/{user_id}/summary")
async def get_user_planner_summary(
    user_id: str,
    db_session: Session = Depends(get_db)
):
    """获取用户规划总结"""
    progress_tracker = ProgressTracker(db_session)
    summary = progress_tracker.get_user_progress_summary(user_id)
    
    return summary

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("[提示] 未检测到OPENAI_API_KEY，请将你的OpenAI API Key写入 backend/.env 文件，如 OPENAI_API_KEY=sk-xxx ...")
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)