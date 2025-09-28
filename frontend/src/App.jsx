import React, { useState, useEffect } from "react";
import JobSelector from "./components/JobSelector";
import JobDescUpload from "./components/JobDescUpload";
import ChatWindow from "./components/ChatWindow";
import InterviewSession from "./components/InterviewSession";
import FeedbackPanel from "./components/FeedbackPanel";

import CivilServiceSelector from "./components/CivilServiceSelector";
import CivilServiceInterview from "./components/CivilServiceInterview";
import Latex from 'react-latex-next';
import {
  FaRocket
} from 'react-icons/fa';
import './App.css';



// 导航组件
function Navigation({ currentView, onNavigate, showBackButton = false }) {
  return (
    <nav className="app-navigation">
      {showBackButton && (
        <button 
          className="nav-back-btn"
          onClick={() => onNavigate("interview")}
        >
          <span className="nav-icon">←</span>
          返回主页
        </button>
      )}
      <div className="nav-tabs">
        <button 
          className={`nav-tab ${currentView === "interview" ? "active" : ""}`}
          onClick={() => onNavigate("interview")}
        >
          <span className="nav-icon">🎯</span>
          智能面试
        </button>

        <button 
          className={`nav-tab ${currentView === "civil-service" ? "active" : ""}`}
          onClick={() => onNavigate("civil-service")}
        >
          <span className="nav-icon">🏛️</span>
          考公面试
        </button>
      </div>
    </nav>
  );
}

// 进度指示器组件
function ProgressIndicator({ currentStep, totalSteps, steps }) {
  return (
    <div className="progress-indicator">
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${(currentStep / totalSteps) * 100}%` }}
        />
      </div>
      <div className="progress-steps">
        {steps.map((step, index) => (
          <div 
            key={index}
            className={`progress-step ${index < currentStep ? "completed" : index === currentStep ? "current" : ""}`}
          >
            <div className="step-dot">
              {index < currentStep ? "✓" : index + 1}
            </div>
            <span className="step-label">{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// 加载状态组件
function LoadingSpinner({ message = "加载中..." }) {
  return (
    <div className="loading-spinner">
      <div className="spinner"></div>
      <p className="loading-message">{message}</p>
    </div>
  );
}

function StepBadge({ step }) {
  return (
    <div className="step-badge">{step}</div>
  );
}

function InterviewHelper() {
  // 添加Interview Planner状态
  const [currentView, setCurrentView] = useState("interview"); // "interview" or "civil-service"
  const [isLoading, setIsLoading] = useState(false);
  const [showNavigation, setShowNavigation] = useState(false);
  
  // JD内容和面试入口状态提升到App级别
  const [jobTitle, setJobTitle] = useState("");   // 选中的岗位
  const [jdText, setJdText] = useState("");
  const [jdUploaded, setJdUploaded] = useState(false);
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [skipJD, setSkipJD] = useState(false);
  const [interviewEnded, setInterviewEnded] = useState(false);
  const [mode, setMode] = useState("chat"); // "chat" | "session"
  
  // 考公面试状态
  const [civilServiceConfig, setCivilServiceConfig] = useState(null);
  const [civilServiceStarted, setCivilServiceStarted] = useState(false);

  // 面试反馈（由ChatWindow传递）
  const [feedback, setFeedback] = useState(null);
  const [improvements, setImprovements] = useState([]);
  const [finalFeedback, setFinalFeedback] = useState({ feedback: null, improvements: [] });

  // 面试准备建议区状态
  const [advice, setAdvice] = useState("");
  const [adviceLoading, setAdviceLoading] = useState(false);
  const [adviceError, setAdviceError] = useState("");

  // 进度步骤定义
  const interviewSteps = [
    "选择职位",
    "上传JD",
    "开始面试",
    "完成面试"
  ];

  // 计算当前步骤
  const getCurrentStep = () => {
    if (interviewEnded) return 4;
    if (interviewStarted) return 3;
    if (jdUploaded) return 2;
    if (jobTitle) return 1;
    return 0;
  };

  // 导航处理
  const handleNavigate = (view) => {
    setIsLoading(true);
    setTimeout(() => {
      setCurrentView(view);
      setIsLoading(false);
    }, 300);
  };

  // 显示导航栏的条件
  useEffect(() => {
    setShowNavigation(currentView !== "interview" || interviewStarted);
  }, [currentView, interviewStarted]);

  // 处理JD上传/粘贴
  const handleJDSubmit = (jd) => {
    setJdText(jd);
    setJdUploaded(true);
  };

  // 处理“面试建议”按钮回调
  const handleAdvice = ({ advice, loading, error }) => {
    setAdvice(advice);
    setAdviceLoading(loading);
    setAdviceError(error);
  };

  // 进入面试
  const handleStartInterview = () => {
    setInterviewStarted(true);
    setSkipJD(false);
    setInterviewEnded(false);
    setFinalFeedback({ feedback: null, improvements: [] });
  };
  // 跳过JD直接面试
  const handleSkipJD = () => {
    setInterviewStarted(true);
    setSkipJD(true);
    setJdText("");
    setInterviewEnded(false);
    setFinalFeedback({ feedback: null, improvements: [] });
  };
  // 结束面试
  const handleEndInterview = () => {
    setInterviewEnded(true);
    setFinalFeedback({ feedback, improvements });
  };

  // 处理AI返回内容，若为JSON则只显示question
  function parseAIResponse(aiText) {
    if (!aiText) return "AI未返回问题。";
    try {
      // 兼容gpt输出带markdown代码块
      let txt = aiText.trim();
      if (txt.startsWith('```json')) txt = txt.replace(/^```json/, '').replace(/```$/, '').trim();
      const parsed = JSON.parse(txt);
      if (parsed.question) return parsed.question;
      return aiText;
    } catch {
      return aiText;
    }
  }



  // 如果当前视图是考公面试，返回考公面试组件
  if (currentView === "civil-service") {
    if (!civilServiceStarted) {
      return (
        <div className="app-wrapper">
          {showNavigation && (
            <Navigation 
              currentView={currentView} 
              onNavigate={handleNavigate}
              showBackButton={true}
          />
          )}
          <CivilServiceSelector 
            onSelect={(config) => {
              setCivilServiceConfig(config);
              setCivilServiceStarted(true);
            }}
            selectedConfig={civilServiceConfig}
          />
        </div>
      );
    } else {
      return (
        <div className="app-wrapper">
          {showNavigation && (
            <Navigation 
              currentView={currentView} 
              onNavigate={handleNavigate}
              showBackButton={true}
            />
          )}
          <CivilServiceInterview 
            examConfig={civilServiceConfig}
            onFeedback={setFeedback}
            onImprovements={setImprovements}
            interviewEnded={interviewEnded}
          />
        </div>
      );
    }
  }

  return (
    <>
      {isLoading && <LoadingSpinner message="页面切换中..." />}
      
      {showNavigation && (
        <Navigation 
          currentView={currentView} 
          onNavigate={handleNavigate}
          showBackButton={false}
        />
      )}

      {/* 背景光斑装饰 */}
      <div className="radial-light-circle top-right" />
      <div className="radial-light-circle bottom-left" />

      {/* 顶部 hero 横幅 */}
      <div className="hero">
        <div className="hero-bg">
          {/* 渐变背景和波浪SVG */}
          <div className="hero-gradient"></div>
          <svg className="hero-wave" viewBox="0 0 1440 18" fill="none">
            <path fill="url(#waveGrad)" d="M0,8 C360,18 1080,0 1440,12 L1440,18 L0,18 Z"/>
            <defs>
              <linearGradient id="waveGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#38bdf8"/>
                <stop offset="100%" stopColor="#6366f1"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div className="hero-content">
          <div className="hero-title">
            <span className="icon-title enhanced-icon">
              <FaRocket className="w-5 h-5" />
            </span>
            Interview Helper
          </div>
          <div className="hero-subtitle">
            AI智能面试陪练，助你高效提升面试表现
          </div>
          {/* 考公面试入口按钮 */}
          <div className="hero-actions">
            <button 
              className="civil-service-entry-btn"
              onClick={() => handleNavigate("civil-service")}
            >
              🏛️ 考公面试
            </button>
          </div>
        </div>
      </div>

      {/* 固定进度指示器 - 始终显示 */}
      <div className="fixed-progress-indicator">
        <ProgressIndicator 
          currentStep={getCurrentStep()}
          totalSteps={interviewSteps.length}
          steps={interviewSteps}
        />
      </div>
      
      <div className="app-container fade-in">
        <div className="card">
          <div className="subtitle" />
          
          {/* Step 1: 选择目标职位 */}
          <section className="container mx-auto max-w-[min(96vw,1600px)] px-3 sm:px-4 md:px-6 lg:px-8 xl:px-10 mt-8">
            <div className="bg-white rounded-2xl p-6 md:p-8 xl:p-12 shadow-lg ring-1 ring-black/5">
              {/* Step标识 - 移到标题上方左对齐 */}
              <div className="mb-6">
                <div className="inline-block bg-gradient-to-br from-indigo-100 to-indigo-200 text-indigo-700 px-4 py-2 rounded-2xl shadow-lg text-lg font-bold">
                  Step 1
                </div>
              </div>
              
              {/* 标题行 - 左侧加图标 */}
              <div className="flex items-center gap-3 mb-8">
                <span className="text-2xl">👤</span>
                <h2 className="text-[clamp(20px,2.2vw,28px)] font-bold text-gray-900 transform translate-y-1.5">
                  选择目标职位
                </h2>
              </div>
              
              {/* 主体内容 - 居中对齐 */}
              <div className="max-w-4xl mx-auto">
                <JobSelector onSelect={setJobTitle} selectedJob={jobTitle} />
              </div>
            </div>
          </section>
          {/* Step 2: 上传职位描述 */}
          <section className="container mx-auto max-w-[min(96vw,1600px)] px-3 sm:px-4 md:px-6 lg:px-8 xl:px-10 mt-8">
            <div className="bg-white rounded-2xl p-6 md:p-8 xl:p-12 shadow-lg ring-1 ring-black/5">
              {/* Step标识 - 移到标题上方左对齐 */}
              <div className="mb-6">
                <div className="inline-block bg-gradient-to-br from-green-100 to-green-200 text-green-700 px-4 py-2 rounded-2xl shadow-lg text-lg font-bold">
                  Step 2
                </div>
              </div>
              
              {/* 标题行 - 左侧加图标 */}
              <div className="flex items-center gap-3 mb-8">
                <span className="text-2xl">📄</span>
                <h2 className="text-[clamp(20px,2.2vw,28px)] font-bold text-gray-900 transform translate-y-1.5">
                  上传职位描述
                </h2>
              </div>
              
              {/* 主体内容 - 居中对齐 */}
              <div className="max-w-4xl mx-auto">
                <JobDescUpload onJDSubmit={handleJDSubmit} onAdvice={handleAdvice} />
              </div>
            </div>
          </section>
                      {advice && !interviewStarted && (
            <section className="container mx-auto max-w-[min(96vw,1600px)] px-3 sm:px-4 md:px-6 lg:px-8 xl:px-10 mt-8">
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 md:p-8 xl:p-12 shadow-lg ring-1 ring-black/5">
                {/* 标题行 - 左侧加图标 */}
                <div className="flex items-center gap-3 mb-8">
                  <span className="text-2xl">💡</span>
                  <h3 className="text-[clamp(20px,2.2vw,28px)] font-bold text-blue-900">
                    面试准备建议
                  </h3>
                </div>
                {/* 主体内容 - 居中对齐 */}
                <div className="max-w-4xl mx-auto text-blue-800 leading-relaxed">
                  {adviceLoading ? '建议生成中...' : adviceError ? adviceError : <Latex>{advice}</Latex>}
                </div>
              </div>
            </section>
          )}
          <section className="container mx-auto max-w-[min(96vw,1600px)] px-3 sm:px-4 md:px-6 lg:px-8 xl:px-10 mt-8">
            <div className="max-w-xl mx-auto">
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={handleStartInterview}
                  disabled={!jdUploaded}
                  className={`inline-flex items-center justify-center gap-2 w-full sm:w-auto h-11 px-6 text-base rounded-lg font-semibold transition-all duration-300 ${
                    jdUploaded 
                      ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-lg hover:shadow-xl hover:-translate-y-1' 
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  <FaRocket className="w-5 h-5" /> 开始模拟面试
                </button>
                <button
                  onClick={handleSkipJD}
                  className="inline-flex items-center justify-center gap-2 w-full sm:w-auto h-11 px-6 text-base rounded-lg font-semibold border-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50 transition-all duration-300"
                >
                  💻 直接开始面试
                </button>
              </div>
            </div>
          </section>
          {/* Step 3: 选择面试体验模式 */}
          {interviewStarted && (
            <section className="container mx-auto max-w-[min(96vw,1600px)] px-3 sm:px-4 md:px-6 lg:px-8 xl:px-10 mt-8">
              <div className="bg-white rounded-2xl p-6 md:p-8 xl:p-12 shadow-lg ring-1 ring-black/5">
                {/* Step标识 - 移到标题上方左对齐 */}
                <div className="mb-6">
                  <div className="inline-block bg-gradient-to-br from-blue-100 to-blue-200 text-blue-700 px-4 py-2 rounded-2xl shadow-lg text-lg font-bold">
                    Step 3
                  </div>
                </div>
                
                {/* 标题行 - 左侧加图标 */}
                <div className="flex items-center gap-3 mb-8">
                  <span className="text-2xl">🎤</span>
                  <h3 className="text-[clamp(20px,2.2vw,28px)] font-bold text-gray-900 transform translate-y-1.5">
                    面试体验模式
                  </h3>
                </div>
                {/* 主体内容 - 居中对齐 */}
                <div className="max-w-3xl mx-auto">
                  <div className="flex flex-col sm:flex-row gap-6">
                    <label className="flex items-center gap-3 cursor-pointer hover:text-indigo-600 transition-colors p-3 rounded-lg hover:bg-indigo-50">
                      <input
                        type="radio"
                        checked={mode === "chat"}
                        onChange={() => setMode("chat")}
                        className="w-5 h-5 text-indigo-600"
                      />
                      <span className="text-lg">文字/语音一体化体验</span>
                    </label>
                    <label className="flex items-center gap-3 cursor-pointer hover:text-indigo-600 transition-colors p-3 rounded-lg hover:bg-indigo-50">
                      <input
                        type="radio"
                        checked={mode === "session"}
                        onChange={() => setMode("session")}
                        className="w-5 h-5 text-indigo-600"
                      />
                      <span className="text-lg">沉浸式语音面试</span>
                    </label>
                  </div>
                </div>
              </div>
            </section>
          )}
          {interviewStarted && (
            <section className="container mx-auto max-w-[min(96vw,1600px)] px-3 sm:px-4 md:px-6 lg:px-8 xl:px-10 mt-8">
              {/* 主体内容 - 直接显示组件，移除外层卡片 */}
              <div className="w-full">
                {mode === "chat" ? (
                  <ChatWindow
                    jobTitle={jobTitle}
                    jdText={skipJD ? null : jdText}
                    onFeedback={setFeedback}
                    onImprovements={setImprovements}
                    interviewEnded={interviewEnded}
                  />
                ) : (
                  <InterviewSession 
                  jobTitle={jobTitle}
                  jdText={skipJD ? "" : jdText}
                  onFeedback={setFeedback}
                  onImprovements={setImprovements}
                  parseAIResponse={parseAIResponse}
                  interviewEnded={interviewEnded}/>
                )}
                {/* 结束面试按钮 - 右对齐 */}
                <div className="mt-6 text-right">
                  {!interviewEnded && (
                    <button 
                      onClick={handleEndInterview} 
                      className="px-8 py-3 bg-red-400 text-white rounded-xl font-semibold hover:bg-red-500 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                    >
                      🛑 结束面试
                    </button>
                  )}
                </div>
              </div>
            </section>
          )}


          {/* 面试反馈区放最底部，结束面试后才显示 */}
          <div style={{ marginTop: 40 }}>
            <div style={{ color: '#888', fontSize: 15, marginBottom: 6 }}>提示：面试反馈将在结束面试后给出</div>
            {interviewEnded && (
              <FeedbackPanel feedback={finalFeedback.feedback} improvements={finalFeedback.improvements} />
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default InterviewHelper;