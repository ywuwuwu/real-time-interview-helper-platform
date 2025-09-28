import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Upload, Send, User, Bot, Briefcase, MessageSquare, BarChart3, Volume2, FileAudio } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api';

// API helper functions
const api = {
  async listJobs() {
    const res = await fetch(`${API_BASE_URL}/jobs`);
    return res.json();
  },
  
  async startSession(jobTitle) {
    const res = await fetch(`${API_BASE_URL}/sessions/start?job_title=${jobTitle}`, {
      method: 'POST'
    });
    return res.json();
  },
  
  async sendToRAG(data) {
    const res = await fetch(`${API_BASE_URL}/rag`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },
  
  async transcribeAudio(audioBlob) {
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.webm');
    const res = await fetch(`${API_BASE_URL}/transcribe`, {
      method: 'POST',
      body: formData
    });
    return res.json();
  },
  
  async textToSpeech(text) {
    const res = await fetch(`${API_BASE_URL}/tts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    return res.blob();
  }
};

export default function InterviewHelper() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const messagesEndRef = useRef(null);
  const audioFileInputRef = useRef(null);

  useEffect(() => {
    loadJobs();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadJobs = async () => {
    try {
      const data = await api.listJobs();
      setJobs(data.jobs);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    }
  };

  const startInterview = async () => {
    if (!selectedJob) return;
    
    try {
      const { session_id } = await api.startSession(selectedJob);
      setSessionId(session_id);
      setMessages([{
        id: Date.now(),
        type: 'bot',
        content: `Great! Let's start your ${selectedJob} interview practice. Tell me about yourself and why you're interested in this role.`
      }]);
    } catch (error) {
      console.error('Failed to start session:', error);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await processAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const processAudio = async (audioBlob) => {
    setIsLoading(true);
    try {
      const { text } = await api.transcribeAudio(audioBlob);
      await sendMessage(text);
    } catch (error) {
      console.error('Failed to process audio:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (text) => {
    if (!text.trim() || !sessionId) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: text
    };
    setMessages(prev => [...prev, userMessage]);
    setTextInput('');
    setIsLoading(true);

    try {
      const response = await api.sendToRAG({
        user_input: text,
        job_title: selectedJob,
        session_id: sessionId
      });

      // Add AI response
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        content: response.ai_response
      }]);

      // Update feedback
      setFeedback({
        ...response.feedback,
        score: response.score,
        improvements: response.suggested_improvements
      });

      // Play audio response (optional)
      // const audioBlob = await api.textToSpeech(response.ai_response);
      // const audioUrl = URL.createObjectURL(audioBlob);
      // new Audio(audioUrl).play();
      
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_title', selectedJob);

    try {
      const res = await fetch(`${API_BASE_URL}/upload-job-desc`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      console.log('Upload successful:', data);
      setShowUpload(false);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  // 新增：处理音频文件上传
  const handleAudioFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // 类型校验
    const allowedTypes = ['audio/mp3', 'audio/wav', 'audio/mpeg', 'audio/wave'];
    if (!allowedTypes.includes(file.type)) {
      alert('请选择MP3或WAV音频文件');
      return;
    }
    // 大小校验
    if (file.size > 10 * 1024 * 1024) {
      alert('文件不能超过10MB');
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API_BASE_URL}/transcribe`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.text) {
        await sendMessage(data.text);
      } else {
        alert('转写失败');
      }
    } catch (e) {
      alert('上传或转写失败');
    } finally {
      setIsLoading(false);
      if (audioFileInputRef.current) audioFileInputRef.current.value = '';
    }
  };

  const triggerAudioFileUpload = () => {
    audioFileInputRef.current?.click();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <MessageSquare className="text-blue-600" />
              Interview Helper
            </h1>
            {sessionId && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Briefcase size={16} />
                <span>Practicing for: {selectedJob}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Chat Area */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border">
              {!sessionId ? (
                // Job Selection Screen
                <div className="p-8">
                  <h2 className="text-xl font-semibold mb-6">Select a Job to Practice</h2>
                  <div className="space-y-4">
                    <select
                      value={selectedJob}
                      onChange={(e) => setSelectedJob(e.target.value)}
                      className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Choose a job title...</option>
                      {jobs.map((job) => (
                        <option key={job.title} value={job.title}>
                          {job.title} - {job.category}
                        </option>
                      ))}
                    </select>

                    <div className="flex gap-4">
                      <button
                        onClick={startInterview}
                        disabled={!selectedJob}
                        className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
                      >
                        Start Interview Practice
                      </button>
                      <button
                        onClick={() => setShowUpload(!showUpload)}
                        className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                      >
                        <Upload size={20} />
                      </button>
                    </div>

                    {showUpload && (
                      <div className="mt-4 p-4 border-2 border-dashed rounded-lg">
                        <input
                          type="file"
                          onChange={handleFileUpload}
                          accept=".pdf,.txt,.docx"
                          className="w-full"
                        />
                        <p className="text-sm text-gray-600 mt-2">
                          Upload a job description to customize your practice
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                // Chat Interface
                <>
                  <div className="h-96 overflow-y-auto p-4 space-y-4">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex gap-3 ${
                          message.type === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        {message.type === 'bot' && (
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                            <Bot size={16} className="text-blue-600" />
                          </div>
                        )}
                        <div
                          className={`max-w-md px-4 py-2 rounded-lg ${
                            message.type === 'user'
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          {message.content}
                        </div>
                        {message.type === 'user' && (
                          <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                            <User size={16} className="text-gray-600" />
                          </div>
                        )}
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex gap-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <Bot size={16} className="text-blue-600" />
                        </div>
                        <div className="bg-gray-100 px-4 py-2 rounded-lg">
                          <div className="flex gap-1">
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></span>
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></span>
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Input Area */}
                  <div className="border-t p-4">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={textInput}
                        onChange={(e) => setTextInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage(textInput)}
                        placeholder="Type your answer..."
                        className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={isLoading}
                      />
                      <button
                        onClick={() => sendMessage(textInput)}
                        disabled={isLoading || !textInput.trim()}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                      >
                        <Send size={20} />
                      </button>
                      <button
                        onClick={isRecording ? stopRecording : startRecording}
                        disabled={isLoading}
                        className={`px-4 py-2 rounded-lg ${
                          isRecording
                            ? 'bg-red-600 hover:bg-red-700 text-white'
                            : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                        }`}
                        title={isRecording ? 'Stop Recording' : 'Start Recording'}
                      >
                        {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
                      </button>
                      {/* 新增：音频文件上传按钮 */}
                      <button
                        onClick={triggerAudioFileUpload}
                        disabled={isLoading}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                        title="上传音频文件（MP3/WAV）"
                      >
                        <FileAudio size={20} />
                      </button>
                    </div>
                    {/* 隐藏的文件输入 */}
                    <input
                      ref={audioFileInputRef}
                      type="file"
                      accept=".mp3,.wav,.mpeg,.wave"
                      onChange={handleAudioFileUpload}
                      style={{ display: 'none' }}
                    />
                    {/* 小提示 */}
                    <div className="mt-2 text-xs text-gray-500">
                      支持上传MP3/WAV音频文件（最大10MB），自动转写为文字
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Feedback Panel */}
          {sessionId && (
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <BarChart3 className="text-blue-600" />
                  Real-time Feedback
                </h3>
                
                {feedback ? (
                  <div className="space-y-4">
                    {/* Score */}
                    {feedback.score && (
                      <div className="text-center">
                        <div className="text-3xl font-bold text-blue-600">
                          {Math.round(feedback.score * 100)}%
                        </div>
                        <div className="text-sm text-gray-600">Overall Score</div>
                      </div>
                    )}

                    {/* Feedback Categories */}
                    <div className="space-y-3">
                      {Object.entries(feedback).filter(([key]) => 
                        !['score', 'improvements'].includes(key)
                      ).map(([category, comment]) => (
                        <div key={category} className="border-l-4 border-blue-500 pl-3">
                          <h4 className="font-medium text-sm capitalize">{category}</h4>
                          <p className="text-sm text-gray-600">{comment}</p>
                        </div>
                      ))}
                    </div>

                    {/* Improvements */}
                    {feedback.improvements && feedback.improvements.length > 0 && (
                      <div>
                        <h4 className="font-medium text-sm mb-2">Suggestions:</h4>
                        <ul className="space-y-1">
                          {feedback.improvements.map((improvement, idx) => (
                            <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                              <span className="text-blue-600 mt-1">•</span>
                              <span>{improvement}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">
                    Start answering questions to receive feedback
                  </p>
                )}
              </div>

              {/* Tips */}
              <div className="mt-4 bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-sm mb-2">Quick Tips</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Use the STAR method for behavioral questions</li>
                  <li>• Be specific with examples and metrics</li>
                  <li>• Keep answers concise (2-3 minutes)</li>
                  <li>• Practice speaking clearly and confidently</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}