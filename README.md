# Interview Helper — Voice-First AI Interview Practice (RAG + Streaming + Production Deployment)

Interview Helper is an AI-powered platform for **voice-driven, personalized interview preparation**.  
It delivers **real-time, streaming responses** and **actionable feedback** grounded in job-specific materials via **Retrieval-Augmented Generation (RAG)**.

This project is intentionally built like a production system (API + streaming UX + reverse proxy + observability + CI/CD + scalable deployment) to demonstrate end-to-end engineering skills—not just a demo chatbot.


- **Real-time streaming UX**: token-by-token / incremental responses for low perceived latency and a natural “live coach” feel.
- **RAG grounded answers**: answers and feedback incorporate job description, company context, and uploaded materials to reduce hallucinations and increase relevance.
- **Voice pipeline**: ASR (speech → text) + TTS (text → speech) for hands-free interview practice.
- **Production deployment ready**:
  - Reverse-proxied behind **Nginx** for stable routing and streaming-friendly settings
  - Containerized with **Docker**
  - Deployable on **Kubernetes** (Deployment + Service)
- **Observability built-in**: `/metrics` endpoint for Prometheus scraping + Grafana dashboards for latency/QPS/error rate.
- **MLOps lifecycle management**: MLflow experiment tracking + model registry versioning (supports rollback).

---

## Feature Overview

### Practice Modes
- **Voice & text** interview practice
- Behavioral, technical, and cultural-fit modules
- Customizable question sets (by job role, company, and uploaded documents)
- “Interview coach” feedback (strengths, gaps, rewrite suggestions, next-step drills)

### Feedback & Analytics
- Personalized, structured feedback (STAR improvements, clarity, impact, conciseness)
- Progress tracking and analytics across sessions
- Repeatable practice loops (question → answer → critique → improved answer)

### Coming Soon
- Peer review workflows
- Mock panel mode (multi-interviewer simulation)

---

## Tech Stack

**Backend**
- Python API server (FastAPI-style)
- RAG pipeline (ingestion → chunking → retrieval → prompt grounding)
- ASR module for voice transcription
- TTS module for voice playback
- Metrics endpoint for monitoring

**Frontend**
- React UI for chat, voice recording, job selection, and feedback panels

**Infra / Ops**
- Docker containerization
- Nginx reverse proxy (streaming-friendly)
- CI via GitHub Actions (tests + build image)
- Kubernetes manifests (Deployment + Service)
- Prometheus + Grafana monitoring (latency/QPS/error rate dashboards)
- MLflow for experiment tracking + model registry versioning

---

## System Architecture (High Level)

**User Flow (Voice)**
1. User records audio in the browser
2. Backend ASR transcribes speech → text
3. RAG retrieves relevant job/company materials
4. LLM generates response + structured feedback
5. Response streams back to UI in real time
6. (Optional) TTS converts response text → audio for playback
7. Session events/metrics are recorded for analytics & monitoring

**Key Engineering Techniques**
- Streaming response protocol (SSE/chunked HTTP or websocket-style streaming)
- Prompt grounding with retrieved context
- Pluggable ASR/TTS backends via environment variables
- Metrics-first design for production debugging

---

## Repository Layout

```text
interview-helper/
├── README.md
├── .gitignore
├── requirements.txt            # Backend dependencies
├── backend/
│   ├── app.py                  # Main backend entrypoint
│   ├── asr/                    # Automatic Speech Recognition (Voice → Text)
│   ├── rag/                    # Retrieval-Augmented Generation pipeline
│   ├── tts/                    # Text-to-Speech (Text → Voice)
│   ├── jobs/
│   │   └── job_knowledge_base/ # Job-specific knowledge base files
│   ├── models/                 # Pre-trained/fine-tuned models (optional)
│   ├── utils/                  # Helpers/utilities
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

