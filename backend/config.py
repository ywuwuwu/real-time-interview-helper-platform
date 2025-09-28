import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    UPLOAD_DIR = BASE_DIR / "uploads"
    MODELS_DIR = BASE_DIR / "models"
    KNOWLEDGE_BASE_DIR = BASE_DIR / "jobs" / "job_knowledge_base"
    
    # Create directories if they don't exist
    UPLOAD_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # API Keys (from environment)
    WHISPER_API_KEY = os.getenv("WHISPER_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Server configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    
    # Model settings
    DEFAULT_ASR_BACKEND = os.getenv("DEFAULT_ASR_BACKEND", "whisper")
    DEFAULT_ASR_MODEL   = os.getenv("ASR_MODEL", "whisper-1")
    LLM_MODEL         = os.getenv("LLM_MODEL", "gpt-4o-mini")    # 使用可用的模型
    DEFAULT_LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")    # 使用可用的模型
    DEFAULT_TTS_VOICE = os.getenv("TTS_VOICE", "alloy")
    
    # Interview settings
    MAX_INTERVIEW_DURATION = int(os.getenv("MAX_INTERVIEW_DURATION", "3600"))  # seconds
    MAX_QUESTIONS_PER_SESSION = int(os.getenv("MAX_QUESTIONS_PER_SESSION", "15"))
    
    # Database settings (for future implementation)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./interview_helper.db")
    
    # File upload settings
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB in bytes
    ALLOWED_EXTENSIONS = {"pdf", "txt", "docx", "doc"}
    
    # Feedback scoring weights
    SCORING_WEIGHTS = {
        "structure": 0.25,
        "content": 0.35,
        "relevance": 0.25,
        "clarity": 0.15
    }
    
    # Interview question templates by type
    QUESTION_TEMPLATES = {
        "behavioral": [
            "Tell me about a time when you {scenario}",
            "How do you handle {situation}?",
            "Describe a situation where you {action}",
            "Give me an example of {skill} in action"
        ],
        "technical": [
            "How would you design {system}?",
            "Explain {concept} to a non-technical person",
            "What's your approach to {technical_challenge}?",
            "Walk me through your solution for {problem}"
        ],
        "situational": [
            "What would you do if {hypothetical}?",
            "How would you prioritize {tasks}?",
            "Imagine you're faced with {scenario}. How would you respond?"
        ]
    }
    
    @classmethod
    def get_env_list(cls, key: str, default: list | None = None) -> list:
        """Get list from environment variable"""
        value = os.getenv(key)
        if value:
            return [item.strip() for item in value.split(",")]
        return default or []

config = Config()