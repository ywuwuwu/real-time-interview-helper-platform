# Interview Helper: Next-Gen AI Interview Practice

An AI-powered platform for voice-driven, personalized interview prep with real-time feedback.

## Features
- Voice & text interview practice
- Customizable question sets (by job, company, uploaded materials)
- Personalized, actionable feedback
- Progress tracking and analytics
- Behavioral, technical, and cultural-fit modules
- Peer review and mock panel modes (coming soon!)

## Getting Started

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py

interview-helper/
├── README.md
├── .gitignore
├── requirements.txt            # Backend dependencies
├── backend/
│   ├── app.py                  # Main backend entrypoint (Flask/FastAPI)
│   ├── asr/                    # Automatic Speech Recognition (Voice → Text)
│   ├── rag/                    # Retrieval-Augmented Generation pipeline
│   ├── tts/                    # Text-to-Speech (Text → Voice)
│   ├── jobs/
│   │   └── job_knowledge_base/ # Job-specific knowledge base files
│   ├── models/                 # Pre-trained/fine-tuned models if needed
│   ├── utils/                  # Helper functions/utilities
│   └── config.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── JobSelector.jsx
│   │   │   ├── JobDescUpload.jsx
│   │   │   ├── VoiceRecorder.jsx
│   │   │   ├── ChatWindow.jsx
│   │   │   └── FeedbackPanel.jsx
│   │   ├── App.jsx
│   │   └── api.js              # API calls to backend
│   └── package.json
└── docs/
    ├── feature_roadmap.md
    ├── architecture.md
    └── usage_guide.md


## Environment Variables Setup

Before running the backend, please create a `.env` file in the `backend` directory with the following content:

```env
# .env (place this in the backend/ folder)
WHISPER_API_KEY=your-whisper-api-key
OPENAI_API_KEY=your-openai-api-key
DEFAULT_ASR_BACKEND=whisper
ASR_MODEL=whisper-1
LLM_MODEL=gpt-4o-mini
```

> ⚠️ **Do NOT commit your real API keys to git!**  
> Each developer should create their own `.env` file locally.