import React, { useState, useRef, useEffect } from 'react';
import VoiceRecorder from './VoiceRecorder';
import AudioUpload from './AudioUpload';

// 考公面试题目类型
const INTERVIEW_TYPES = [
  {
    id: 'self_intro',
    name: '自我介绍',
    description: '考生自我介绍环节',
    icon: '👤',
    duration: 120, // 秒
    tips: [
      '突出个人优势和特点',
      '结合报考岗位要求',
      '语言表达清晰流畅',
      '时间控制在2分钟内'
    ]
  },
  {
    id: 'policy_analysis',
    name: '政策分析',
    description: '分析当前热点政策',
    icon: '📊',
    duration: 180,
    tips: [
      '准确把握政策要点',
      '分析政策背景和意义',
      '提出建设性建议',
      '体现政治素养'
    ]
  },
  {
    id: 'situation_handling',
    name: '情景处理',
    description: '处理实际工作场景',
    icon: '🎯',
    duration: 150,
    tips: [
      '明确问题核心',
      '制定解决方案',
      '考虑各方利益',
      '体现服务意识'
    ]
  },
  {
    id: 'professional_knowledge',
    name: '专业知识',
    description: '考察岗位专业知识',
    icon: '📚',
    duration: 120,
    tips: [
      '展示专业素养',
      '结合实际案例',
      '体现学习能力',
      '突出实践能力'
    ]
  }
];

const CivilServiceInterview = ({ examConfig, onFeedback, onImprovements, interviewEnded }) => {
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [interviewHistory, setInterviewHistory] = useState([]);
  const [currentStep, setCurrentStep] = useState('preparation'); // preparation, interview, feedback
  const [selectedInterviewType, setSelectedInterviewType] = useState('');
  const [showVoiceTools, setShowVoiceTools] = useState(false);
  const [userAnswer, setUserAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [timer, setTimer] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [improvements, setImprovements] = useState([]);

  const timerRef = useRef(null);

  // 模拟考公面试题目
  const generateQuestion = (interviewType) => {
    const questions = {
      self_intro: [
        "请做一个2分钟的自我介绍，重点介绍你的学习经历、工作经验和报考动机。",
        "请结合你的专业背景和报考岗位，做一个简短的自我介绍。",
        "请介绍一下你的基本情况，并说明为什么选择报考这个岗位。"
      ],
      policy_analysis: [
        "请分析一下当前'放管服'改革的重要意义和主要措施。",
        "如何看待'互联网+政务服务'在提升政府治理能力中的作用？",
        "请谈谈你对'乡村振兴战略'的理解和认识。"
      ],
      situation_handling: [
        "如果群众反映你负责的业务办理流程过于复杂，你会如何处理？",
        "在接待群众时，遇到情绪激动的投诉者，你会怎么应对？",
        "如果领导交办的任务与现有政策有冲突，你会如何处理？"
      ],
      professional_knowledge: [
        "请谈谈你对公务员职业道德的理解。",
        "如何理解'全心全意为人民服务'的宗旨？",
        "请结合报考岗位，谈谈如何提高工作效率和服务质量。"
      ]
    };

    const typeQuestions = questions[interviewType] || [];
    const randomQuestion = typeQuestions[Math.floor(Math.random() * typeQuestions.length)];
    
    return {
      id: Date.now(),
      type: interviewType,
      question: randomQuestion,
      duration: INTERVIEW_TYPES.find(t => t.id === interviewType)?.duration || 120,
      timestamp: new Date().toISOString()
    };
  };

  // 开始面试
  const startInterview = (interviewType) => {
    const question = generateQuestion(interviewType);
    setCurrentQuestion(question);
    setSelectedInterviewType(interviewType);
    setCurrentStep('interview');
    setTimer(0);
    setIsTimerRunning(true);
    setUserAnswer('');
    setFeedback(null);
    setImprovements([]);
  };

  // 提交答案
  const submitAnswer = async () => {
    if (!userAnswer.trim()) {
      alert('请输入你的答案');
      return;
    }

    setIsLoading(true);
    setIsTimerRunning(false);

    // 模拟AI分析
    setTimeout(() => {
      const mockFeedback = {
        content: `你的回答整体表现良好，语言表达清晰，逻辑结构合理。在${INTERVIEW_TYPES.find(t => t.id === selectedInterviewType)?.name}方面展现了较好的素养。`,
        score: Math.floor(Math.random() * 20) + 80, // 80-100分
        strengths: [
          '语言表达清晰流畅',
          '逻辑思维较为清晰',
          '态度诚恳认真'
        ],
        weaknesses: [
          '可以进一步结合具体案例',
          '建议增加政策理论深度',
          '时间控制需要更加精准'
        ]
      };

      const mockImprovements = [
        '建议多关注时事政治，提高政策敏感度',
        '可以准备一些具体的工作案例',
        '加强语言表达的条理性',
        '注意面试礼仪和形象'
      ];

      setFeedback(mockFeedback);
      setImprovements(mockImprovements);
      setCurrentStep('feedback');
      setIsLoading(false);

      // 更新面试历史
      setInterviewHistory(prev => [...prev, {
        question: currentQuestion,
        answer: userAnswer,
        feedback: mockFeedback,
        improvements: mockImprovements,
        duration: timer
      }]);

      // 回调给父组件
      onFeedback?.(mockFeedback);
      onImprovements?.(mockImprovements);
    }, 2000);
  };

  // 处理语音录制完成
  const handleRecordingComplete = (blob, url) => {
    console.log('语音录制完成:', blob, url);
    // 这里可以添加语音转文字的逻辑
    const placeholderText = "[语音回答]";
    setUserAnswer(placeholderText);
  };

  // 处理音频文件上传
  const handleAudioUpload = (file, url) => {
    console.log('音频上传:', file, url);
    // 这里可以添加音频转文字的逻辑
    const placeholderText = "[音频回答]";
    setUserAnswer(placeholderText);
  };

  // 重新开始
  const restartInterview = () => {
    setCurrentStep('preparation');
    setCurrentQuestion(null);
    setSelectedInterviewType('');
    setUserAnswer('');
    setFeedback(null);
    setImprovements([]);
    setTimer(0);
    setIsTimerRunning(false);
  };

  // 计时器
  useEffect(() => {
    if (isTimerRunning) {
      timerRef.current = setInterval(() => {
        setTimer(prev => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isTimerRunning]);

  // 格式化时间
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const selectedTypeData = INTERVIEW_TYPES.find(t => t.id === selectedInterviewType);

  return (
    <div className="civil-service-interview">
      {currentStep === 'preparation' && (
        <div className="interview-preparation">
          <div className="section-card">
            <h2>
              <span className="icon-title enhanced-icon">🏛️</span>
              考公面试练习
            </h2>
            <p className="exam-info">
              {examConfig?.examName} - {examConfig?.province ? `${examConfig.province}地区` : '全国'}
            </p>
          </div>

          <div className="section-card">
            <h3>📋 选择面试类型</h3>
            <div className="interview-types-grid">
              {INTERVIEW_TYPES.map((type) => (
                <div
                  key={type.id}
                  className="interview-type-card"
                  onClick={() => startInterview(type.id)}
                >
                  <div className="type-icon">{type.icon}</div>
                  <div className="type-info">
                    <h4>{type.name}</h4>
                    <p>{type.description}</p>
                    <div className="type-duration">
                      建议时长：{formatTime(type.duration)}
                    </div>
                  </div>
                  <div className="type-tips">
                    <h5>答题要点：</h5>
                    <ul>
                      {type.tips.map((tip, index) => (
                        <li key={index}>{tip}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {currentStep === 'interview' && currentQuestion && (
        <div className="interview-session">
          <div className="section-card">
            <div className="question-header">
              <h2>
                <span className="icon-title enhanced-icon">{selectedTypeData?.icon}</span>
                {selectedTypeData?.name}
              </h2>
              <div className="timer-display">
                <span className="timer-label">答题时间：</span>
                <span className={`timer ${timer > selectedTypeData?.duration ? 'timeout' : ''}`}>
                  {formatTime(timer)}
                </span>
              </div>
            </div>

            <div className="question-content">
              <h3>📝 面试题目</h3>
              <div className="question-text">
                {currentQuestion.question}
              </div>
            </div>

            <div className="answer-section">
              <h3>💬 你的回答</h3>
              <div className="answer-input-area">
                <textarea
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  placeholder="请在此输入你的答案..."
                  className="answer-textarea"
                  rows={6}
                />
                
                <div className="input-controls">
                  <button
                    onClick={() => setShowVoiceTools(!showVoiceTools)}
                    className="btn btn-outline"
                    style={{ minWidth: 80 }}
                  >
                    {showVoiceTools ? "隐藏" : "语音"}
                  </button>
                  
                  <button
                    onClick={submitAnswer}
                    className="btn btn-primary"
                    disabled={!userAnswer.trim() || isLoading}
                  >
                    {isLoading ? '分析中...' : '提交答案'}
                  </button>
                </div>
              </div>

              {/* 语音工具区域 */}
              {showVoiceTools && (
                <div className="voice-tools-area">
                  <h4>🎤 语音输入工具</h4>
                  <div className="voice-tools-grid">
                    <div>
                      <h5>🎙️ 实时录音</h5>
                      <VoiceRecorder
                        onRecordingComplete={handleRecordingComplete}
                        onAudioUpload={handleRecordingComplete}
                      />
                    </div>
                    <div>
                      <h5>📁 音频上传</h5>
                      <AudioUpload
                        onFileSelect={(file, url) => console.log('文件选择:', file, url)}
                        onFileUpload={handleAudioUpload}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {currentStep === 'feedback' && feedback && (
        <div className="interview-feedback">
          <div className="section-card">
            <h2>
              <span className="icon-title enhanced-icon">📊</span>
              面试反馈
            </h2>

            <div className="feedback-content">
              <div className="score-section">
                <h3>📈 综合评分</h3>
                <div className="score-display">
                  <span className="score">{feedback.score}</span>
                  <span className="score-label">分</span>
                </div>
              </div>

              <div className="feedback-details">
                <div className="feedback-section">
                  <h4>✅ 优点表现</h4>
                  <ul>
                    {feedback.strengths.map((strength, index) => (
                      <li key={index}>{strength}</li>
                    ))}
                  </ul>
                </div>

                <div className="feedback-section">
                  <h4>🔧 改进建议</h4>
                  <ul>
                    {feedback.weaknesses.map((weakness, index) => (
                      <li key={index}>{weakness}</li>
                    ))}
                  </ul>
                </div>

                <div className="feedback-section">
                  <h4>💡 提升建议</h4>
                  <ul>
                    {improvements.map((improvement, index) => (
                      <li key={index}>{improvement}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="feedback-summary">
                <p>{feedback.content}</p>
              </div>
            </div>

            <div className="action-buttons">
              <button
                onClick={restartInterview}
                className="btn btn-primary btn-fancy"
              >
                <span className="btn-icon">🔄</span>
                重新练习
              </button>
              <button
                onClick={() => setCurrentStep('preparation')}
                className="btn btn-outline btn-fancy"
              >
                <span className="btn-icon">📋</span>
                选择其他类型
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CivilServiceInterview; 