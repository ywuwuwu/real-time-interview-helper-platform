import React, { useState, useRef, useEffect } from "react";
import { useInterviewWebSocket } from "../api";
import VoiceRecorder from "./VoiceRecorder";
import AudioUpload from "./AudioUpload";


function useStreamAudioPlayer() {

  const mediaSourceRef = useRef(null);
  const sourceBufferRef = useRef(null);
  const audioRef = useRef(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const mediaSource = new window.MediaSource();
    mediaSourceRef.current = mediaSource
    const url = URL.createObjectURL(mediaSourceRef.current);
    audioRef.current = new Audio(url);
    function handleSourceOpen() {
      if (mediaSource.readyState === "open" && !sourceBufferRef.current) {
        sourceBufferRef.current = mediaSource.addSourceBuffer("audio/mpeg");
        setIsReady(true);
      }
    }
    mediaSource.addEventListener("sourceopen", handleSourceOpen);
  
    return () => {
      audioRef.current && audioRef.current.pause();
      audioRef.current = null;
      mediaSource.removeEventListener("sourceopen", handleSourceOpen);
    };
  }, []);

  function appendAudioChunk(chunk) {
    if (!sourceBufferRef.current) return;
    if (sourceBufferRef.current.updating) {
      setTimeout(() => appendAudioChunk(chunk), 20);
      return;
    }
    try {
      sourceBufferRef.current.appendBuffer(new Uint8Array(chunk));
    } catch (e) {}
  }
  function play() { audioRef.current && audioRef.current.play(); }
  function pause() { audioRef.current && audioRef.current.pause(); }
  function stop() { audioRef.current && audioRef.current.pause(); }
  function download() { /* 略，见前 */ }
  return { audioRef, appendAudioChunk, play, pause, stop, download, isReady };
}

// ==== 主组件 ====
const VOICE_OPTIONS = [
  { value: "alloy", label: "Alloy(中性)" },
  { value: "shimmer", label: "Shimmer(女性)" },
  { value: "echo", label: "Echo(男低音)" },
];

export default function InterviewSession({ jobTitle, jdText, onFeedback, onImprovements, parseAIResponse, interviewEnded }) {
  
  // 1. UI State
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [connectionRetries, setConnectionRetries] = useState(0);

  const [feedbackHistory, setFeedbackHistory] = useState([]);
  const [improvementHistory, setImprovementHistory] = useState([]);
  const [chatHistory, setChatHistory] = useState([]); // {role: "user"|"ai", text}
  const [wsStatus, setWsStatus] = useState("closed");
  const [selectedVoice, setSelectedVoice] = useState("alloy");
  const [welcomeSent, setWelcomeSent] = useState(false);
  const [audioKey, setAudioKey] = useState(0);
  const [showVoiceTools, setShowVoiceTools] = useState(false);
  const [showConnectionStatus, setShowConnectionStatus] = useState(false);
  const { audioRef, appendAudioChunk, play, pause, stop, download, isReady } = useStreamAudioPlayer();
  // 你的自定义 WebSocket hook
  const { connect, sendUserInput, close, wsRef } = useInterviewWebSocket({
    onText: (data) => {
      stop();
      setAudioKey(prev => prev + 1); // 每次触发新audio时，更新audioKey
      setChatHistory(prev => [
        ...prev,
        { role: "ai", text: data.ai_response, feedback: data.feedback, improvements: data.suggested_improvements }
      ]);
      setIsTyping(false);
      setLoading(false);
      //if (isReady) play();
    },
    onAudio: (audioChunk) => {
      appendAudioChunk(audioChunk);
      play();  // 每收到音频 chunk 时，自动尝试播放
    },
    onOpen: () => {
      setWsStatus("open");
      setShowConnectionStatus(false);
      setConnectionRetries(0);
    },
    onClose: () => { 
      setWsStatus("closed"); 
      stop(); 
      setShowConnectionStatus(true);
    },
    onError: () => {
      setWsStatus("error");
      setShowConnectionStatus(true);
      setConnectionRetries(prev => prev + 1);
    },
  });

  // 组件挂载/卸载时只初始化一次连接
  useEffect(() => {
    connect();
    return () => { close(); };
    // eslint-disable-next-line
  }, []);

  // 连接状态管理
  useEffect(() => {
    if (wsStatus === "error" && connectionRetries < 3) {
      const timer = setTimeout(() => {
        connect();
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [wsStatus, connectionRetries, connect]);

  // 自动发送欢迎消息
  useEffect(() => {
    if (wsStatus === "open" && !welcomeSent) {
      const welcomeMessage = jdText 
        ? "欢迎来到定制化模拟面试。请先自我介绍一下。" 
        : "欢迎来到模拟面试。请先自我介绍一下。";
      
      setChatHistory([{ role: "ai", text: welcomeMessage }]);
      setWelcomeSent(true);
    }
  }, [wsStatus, welcomeSent, jdText]);

  // 自动首次发欢迎语（用setTimeout保证ws是最新的）

  useEffect(() => {
    if (wsStatus === "open" && !welcomeSent) {
      setChatHistory([
        { role: "ai", text: "欢迎来到沉浸式AI模拟面试，AI考官将全程陪练。请自我介绍一下。" }
      ]);
      setWelcomeSent(true);
    }
  }, [wsStatus, jobTitle, jdText, selectedVoice]);

  // 发送用户消息
  function handleSend() {
    if (!input.trim() || interviewEnded) return;
    if (!wsRef.current || wsRef.current.readyState !== 1) {
      alert("WebSocket 未连接，不能发送");
      return;
    }
    
    const userMessage = input.trim();
    setChatHistory(prev => [...prev, { role: "user", text: userMessage }]);
    setInput("");
    setLoading(true);
    setIsTyping(true);
    
    sendUserInput({
      user_input: userMessage,
      job_title: jobTitle,
      job_desc: jdText,
      voice: selectedVoice,
      tts_model: "tts-1", 
    });
  }

  // 处理语音录制完成
  function handleRecordingComplete(blob, url) {
    console.log('录音完成:', blob, url);
    // 这里可以添加语音转文字的逻辑
    // 暂时用占位符文本
    const placeholderText = "[语音回答]";
    if (!wsRef.current || wsRef.current.readyState !== 1) {
      alert("WebSocket 未连接，不能发送");
      return;
    }
    sendUserInput({
      user_input: placeholderText,
      job_title: jobTitle,
      job_desc: jdText,
      voice: selectedVoice,
      tts_model: "tts-1", 
    });
    setChatHistory(prev => [...prev, { role: "user", text: placeholderText }]);
  }

  // 处理音频文件上传
  function handleAudioUpload(file, url) {
    console.log('音频上传:', file, url);
    // 这里可以添加音频转文字的逻辑
    // 暂时用占位符文本
    const placeholderText = "[音频回答]";
    if (!wsRef.current || wsRef.current.readyState !== 1) {
      alert("WebSocket 未连接，不能发送");
      return;
    }
    sendUserInput({
      user_input: placeholderText,
      job_title: jobTitle,
      job_desc: jdText,
      voice: selectedVoice,
      tts_model: "tts-1", 
    });
    setChatHistory(prev => [...prev, { role: "user", text: placeholderText }]);
  }

  return (
    <div className="section-card" style={{ maxWidth: 650, margin: "32px auto", background: "#fff" }}>
      <h2 style={{ fontWeight: 700, fontSize: '1.3rem', marginBottom: 18 }}>AI 沉浸式语音面试</h2>
      
      {/* 连接状态显示 */}
      <div className="connection-status">
        <div className="status-indicator">
          <div className={`status-dot ${wsStatus}`}></div>
          <span className="status-text">
            {wsStatus === "open" ? "已连接" : wsStatus === "closed" ? "未连接" : "连接中..."}
          </span>
          {wsStatus === "error" && connectionRetries > 0 && (
            <span className="retry-count">重试 {connectionRetries}/3</span>
          )}
        </div>
        
        <div className="connection-controls">
          <button 
            onClick={connect} 
            disabled={wsStatus === "open"} 
            className="btn btn-primary btn-sm"
          >
            {wsStatus === "open" ? "已连接" : "连接"}
          </button>
          <button 
            onClick={close} 
            disabled={wsStatus !== "open"} 
            className="btn btn-outline btn-sm"
          >
            断开
          </button>
          <select 
            value={selectedVoice} 
            onChange={e => setSelectedVoice(e.target.value)} 
            className="voice-select"
          >
            {VOICE_OPTIONS.map(opt => <option value={opt.value} key={opt.value}>{opt.label}</option>)}
          </select>
        </div>
      </div>

      {/* 连接错误提示 */}
      {showConnectionStatus && wsStatus === "error" && (
        <div className="connection-error">
          <div className="error-icon">⚠️</div>
          <div className="error-content">
            <h4>连接失败</h4>
            <p>无法连接到面试服务器，请检查网络连接后重试。</p>
            <button 
              onClick={connect} 
              className="btn btn-primary"
              disabled={connectionRetries >= 3}
            >
              {connectionRetries >= 3 ? "重试次数已达上限" : "重新连接"}
            </button>
          </div>
        </div>
      )}
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => (e.key === "Enter" ? handleSend() : null)}
          placeholder="请输入你的面试回答…"
          className="input"
          disabled={wsStatus !== "open"}
        />
        <button
          onClick={handleSend}
          className="btn btn-primary"
          disabled={!input.trim() || wsStatus !== "open"}
        >
          发送
        </button>
        <button
          onClick={() => setShowVoiceTools(!showVoiceTools)}
          className="btn btn-outline"
          style={{ minWidth: 80 }}
        >
          {showVoiceTools ? "隐藏" : "语音"}
        </button>
      </div>
      
      {/* 语音工具区域 */}
      {showVoiceTools && (
        <div style={{ 
          marginBottom: 16, 
          padding: "16px", 
          background: "#f8fafc", 
          borderRadius: "8px",
          border: "1px solid #e2e8f0"
        }}>
          <h4 style={{ 
            margin: "0 0 12px 0", 
            fontSize: "1rem", 
            color: "#334155",
            fontWeight: 600
          }}>
            🎤 语音输入工具
          </h4>
          <div style={{ 
            display: "grid", 
            gap: "1rem", 
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))" 
          }}>
            <div>
              <h5 style={{ 
                fontSize: "0.9rem", 
                marginBottom: "0.5rem", 
                color: "#64748b",
                fontWeight: 500
              }}>
                🎙️ 实时录音
              </h5>
              <VoiceRecorder
                onRecordingComplete={handleRecordingComplete}
                onAudioUpload={handleRecordingComplete}
                disabled={wsStatus !== "open"}
              />
            </div>
            <div>
              <h5 style={{ 
                fontSize: "0.9rem", 
                marginBottom: "0.5rem", 
                color: "#64748b",
                fontWeight: 500
              }}>
                📁 音频上传
              </h5>
              <AudioUpload
                onFileSelect={(file, url) => console.log('文件选择:', file, url)}
                onFileUpload={handleAudioUpload}
                disabled={wsStatus !== "open"}
              />
            </div>
          </div>
        </div>
      )}
      <div style={{ minHeight: 180, background: "#f6f8fa", borderRadius: 8, padding: 12, marginBottom: 12 }}>
        {chatHistory.length === 0 && <div style={{ color: "#aaa" }}>暂无对话，快试试输入自我介绍吧！</div>}
        {chatHistory.map((msg, idx) => (
          <div key={idx} style={{
            margin: "12px 0",
            textAlign: msg.role === "user" ? "right" : "left"
          }}>
            <div style={{
              display: "inline-block",
              background: msg.role === "user" ? "#e0e7ef" : "#f1f5f9",
              padding: "10px 18px",
              borderRadius: 14,
              maxWidth: "85%",
              fontWeight: msg.role === "user" ? 500 : 400,
              fontSize: '1.05rem',
              color: msg.role === "user" ? '#334155' : '#2563eb',
              boxShadow: '0 1px 4px rgba(30,41,59,0.04)'
            }}>
              {msg.role === "user" ? <>你：{msg.text}</> : <>
                <div><b>AI：</b>{msg.text}</div>
                {msg.feedback && typeof msg.feedback === "object" && (
                <div style={{ fontSize: 13, marginTop: 2, color: "#444" }}>
                  点评：
                  <ul style={{ margin: 0, padding: 0, listStyle: "none" }}>
                    {Object.entries(msg.feedback).map(([key, value]) => (
                      <li key={key}>
                        <b>{key}：</b>{value}
                      </li>
                    ))}
                  </ul>
                </div>
                )}
                {msg.feedback && typeof msg.feedback === "string" && (
                  <div style={{ fontSize: 13, marginTop: 2, color: "#444" }}>点评：{msg.feedback}</div>
                )}
                {msg.improvements && msg.improvements.length > 0 && (
                  <ul style={{ fontSize: 12, color: "#888" }}>
                    {msg.improvements.map((imp, j) => <li key={j}>{imp}</li>)}
                  </ul>
                )}
              </>}
            </div>
          </div>
        ))}
      </div>
      <div className="audio-bar">
        <button onClick={play} className="btn btn-outline" style={{ minWidth: 60 }}>播放</button>
        <button onClick={pause} className="btn btn-outline" style={{ minWidth: 60 }}>暂停</button>
        <button onClick={stop} className="btn btn-outline" style={{ minWidth: 60 }}>停止</button>
        <button onClick={download} className="btn btn-outline" style={{ minWidth: 90 }}>下载音频</button>
        <audio ref={audioRef} controls style={{ marginLeft: 12, flex: 1 }} />
      </div>
    </div>
  );
}
