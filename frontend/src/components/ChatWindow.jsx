// import React, { useState } from "react";

// function ChatWindow({ jdText, onFeedback, onImprovements, parseAIResponse, interviewEnded }) {
//   const [messages, setMessages] = useState([
//     { role: "ai", content: jdText ? "欢迎来到定制化模拟面试。请先自我介绍一下。" : "欢迎来到模拟面试。请先自我介绍一下。" }
//   ]);
//   const [input, setInput] = useState("");
//   const [loading, setLoading] = useState(false);



//   return (
//     <div style={{ border: '1px solid #ccc', padding: '1rem', minHeight: '200px', borderRadius: 8, marginTop: 20 }}>
//       <div style={{ minHeight: 120, marginBottom: 12 }}>
//         {messages.map((msg, idx) => (
//           <div key={idx} style={{ textAlign: msg.role === "ai" ? "left" : "right", margin: '8px 0' }}>
//             <span style={{ fontWeight: msg.role === "ai" ? 700 : 500, color: msg.role === "ai" ? '#007bff' : '#222' }}>
//               {msg.role === "ai" ? "AI: " : "我: "}
//             </span>
//             <span>{msg.content}</span>
//           </div>
//         ))}
//       </div>
//       <div style={{ display: 'flex', gap: 8 }}>
//         <input
//           type="text"
//           value={input}
//           onChange={e => setInput(e.target.value)}
//           onKeyDown={e => { if (e.key === 'Enter') handleSend(); }}
//           placeholder="输入你的回答..."
//           style={{ flex: 1, borderRadius: 6, border: '1px solid #bbb', padding: 8 }}
//           disabled={loading || interviewEnded}
//         />
//         <button onClick={handleSend} disabled={loading || !input.trim() || interviewEnded} style={{ borderRadius: 6, background: '#007bff', color: '#fff', border: 'none', padding: '8px 18px', fontWeight: 600 }}>
//           {loading ? '发送中...' : '发送'}
//         </button>
//       </div>
//     </div>
//   );
// }

// export default ChatWindow; 

import React, { useState, useRef, useEffect } from "react";
import { fetchRagTTSMultipart, fetchRagTTS, fetchTTS } from "../api";


const VOICE_OPTIONS = [
  { value: "alloy", label: "Alloy(中性)" },
  { value: "shimmer", label: "Shimmer(女性)" },
  { value: "echo", label: "Echo(男低音)" },
];


export default function ChatWindow({ jobTitle, jdText, onFeedback, onImprovements, parseAIResponse, interviewEnded }) {
  // 1. UI State
  const [messages, setMessages] = useState([
    { role: "ai", content: jdText ? "欢迎来到定制化模拟面试。请先自我介绍一下。" : "欢迎来到模拟面试。请先自我介绍一下。" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);

  const [feedbackHistory, setFeedbackHistory] = useState([]);
  const [improvementHistory, setImprovementHistory] = useState([]);

  // 2. 模式/音色
  const [mode, setMode] = useState("text"); // "text" or "audio"
  const [selectedVoice, setSelectedVoice] = useState("alloy");
  const [latestAudioUrl, setLatestAudioUrl] = useState(null);
  
  // 3. 聊天界面状态
  const [showChatTips, setShowChatTips] = useState(false);
  const [messageCount, setMessageCount] = useState(0);
  
  // 4. 音频播放状态
  const [currentAudio, setCurrentAudio] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  
  // 清理音频资源
  useEffect(() => {
    return () => {
      if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        setCurrentAudio(null);
        setIsPlaying(false);
      }
    };
  }, [currentAudio]);


  async function handleSend_text() {
    if (!input.trim() || interviewEnded) return;
    
    const userMsg = { role: "user", content: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");
    setLoading(true);
    setIsTyping(true);
    setShowWelcome(false);
    setMessageCount(prev => prev + 1);
    
    try {
      const body = { user_input: input, job_title: jobTitle };
      if (jdText) body.job_desc = jdText;
      const resp = await fetch("/api/rag", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const data = await resp.json();
      let aiText = data.ai_response || "AI未返回问题。";
      if (parseAIResponse) aiText = parseAIResponse(aiText);
      setMessages((msgs) => [
        ...msgs,
        { role: "ai", content: aiText }
      ]);
      if (onFeedback) onFeedback(data.feedback || null);
      if (onImprovements) onImprovements(data.suggested_improvements || []);
      setIsTyping(false);
    } catch (err) {
      setMessages((msgs) => [
        ...msgs,
        { role: "ai", content: "请求失败，请稍后重试。" }
      ]);
      if (onFeedback) onFeedback(null);
      if (onImprovements) onImprovements([]);
    }
    setLoading(false);
  }

  // 5. 发送消息
  async function handleSend() {
    if (!input.trim() || interviewEnded) return;
    if (mode === "audio") {
      // 语音模式，调用 fetchRagTTS（rag-tts）接口
      setMessages((msgs) => [...msgs, { role: "user", content: input }]);
      setInput("");
      setLoading(true);
      try {
        const result = await fetchRagTTS(input, jobTitle, jdText, selectedVoice, "tts-1");
        setMessages((msgs) => [
          ...msgs,
          { role: "ai", content: result.ragText } // 你可以扩展结构化内容
        ]);
        const url = URL.createObjectURL(result.audioBlob);
        setLatestAudioUrl(url);

        if (result.feedback !== undefined && result.feedback !== null)
          setFeedbackHistory(h => [...h, result.feedback]);
        if (Array.isArray(result.improvements) && result.improvements.length > 0)
          setImprovementHistory(h => [...h, ...result.improvements]);
        // 自动播放（语音模式）
        if (mode === "audio") {
          const audio = new Audio(url);
          audio.play();
        }
        if (onFeedback) onFeedback(result.feedback || null);
        if (onImprovements) onImprovements(result.improvements || []);      
      } catch (e) {
        setMessages((msgs) => 
          [...msgs, { role: "ai", content: "请求失败，请稍后重试。" }]);
        if (onFeedback) onFeedback(null);
        if (onImprovements) onImprovements([]);
      }
      setLoading(false);
    } else {
      // 文字模式，调用 handleSend_text（用 /api/rag）
      await handleSend_text();
    }
  }
  // 6. TTS按钮 - 单条AI消息播报
  async function handleTTS(msg) {
    try {
      // 如果当前有音频在播放，先停止
      if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        setIsPlaying(false);
      }
      
      const blob = await fetchTTS(msg.content, selectedVoice, 1.0);
      const url = URL.createObjectURL(blob);
      
      const audio = new Audio(url);
      
      // 设置音频事件监听器
      audio.addEventListener('ended', () => {
        setIsPlaying(false);
        // 清理URL
        URL.revokeObjectURL(url);
      });
      
      audio.addEventListener('error', () => {
        setIsPlaying(false);
        URL.revokeObjectURL(url);
      });
      
      // 播放音频
      await audio.play();
      setCurrentAudio(audio);
      setIsPlaying(true);
      
    } catch (error) { 
      console.error('TTS播放失败:', error);
      alert("生成语音失败！"); 
    }
  }

  return (
    <div className="chat-window">
      {/* 欢迎提示 */}
      {showWelcome && (
        <div className="welcome-tip">
          <div className="tip-icon">💡</div>
          <div className="tip-content">
            <h4>面试小贴士</h4>
            <p>请保持自然、自信的回答态度。AI会根据您的回答提供实时反馈和建议。</p>
          </div>
        </div>
      )}
      
      {/* 聊天统计 */}
      {messageCount > 0 && (
        <div className="chat-stats">
          <span className="stat-item">对话轮次: {messageCount}</span>
          <span className="stat-item">模式: {mode === "text" ? "文字" : "语音"}</span>
        </div>
      )}
      
      {/* 顶部模式切换 */}
      <div className="chat-controls">
        <div className="mode-selector">
          <span className="control-label">模式：</span>
          <div className="radio-group">
            <label className="radio-option">
              <input 
                type="radio" 
                checked={mode === "text"} 
                onChange={() => setMode("text")} 
              />
              <span className="radio-label">文字模式</span>
            </label>
            <label className="radio-option">
              <input 
                type="radio" 
                checked={mode === "audio"} 
                onChange={() => setMode("audio")} 
              />
              <span className="radio-label">语音模式</span>
            </label>
          </div>
        </div>
        
        <div className="voice-selector">
          <span className="control-label">音色：</span>
          <select 
            value={selectedVoice} 
            onChange={e => setSelectedVoice(e.target.value)} 
            className="voice-select"
          >
            {VOICE_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
          </select>
        </div>
      </div>
      {/* 聊天内容 */}
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.role === "user" ? (
                <div className="user-message">
                  <span className="message-text">{msg.content}</span>
                </div>
              ) : (
                <div className="ai-message">
                  <div className="ai-header">
                    <span className="ai-label">AI面试官</span>
                    {mode === "text" && (
                      <button 
                        onClick={() => handleTTS(msg)} 
                        className={`tts-btn ${isPlaying ? 'playing' : ''}`}
                        title={isPlaying ? "停止播放" : "播放语音"}
                        disabled={isPlaying}
                      >
                        {isPlaying ? '⏹️' : '🔊'}
                      </button>
                    )}
                  </div>
                  <div className="message-text">{msg.content}</div>
                  
                  {/* 展示结构化反馈/建议 */}
                  {msg.feedback && (
                    <div className="feedback-section">
                      <div className="feedback-label">💡 点评</div>
                      <div className="feedback-content">{msg.feedback}</div>
                    </div>
                  )}
                  
                  {msg.improvements && msg.improvements.length > 0 && (
                    <div className="improvements-section">
                      <div className="improvements-label">📝 建议</div>
                      <ul className="improvements-list">
                        {msg.improvements.map((imp, j) => (
                          <li key={j} className="improvement-item">{imp}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {/* 打字指示器 */}
        {isTyping && (
          <div className="typing-indicator">
            <span>AI正在思考</span>
            <div className="typing-dots">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        )}
      </div>
      {/* 输入区 */}
      <div className="chat-input-area">
        <div className="input-wrapper">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleSend(); }}
            placeholder="输入你的回答..."
            className="chat-input"
            disabled={loading || interviewEnded}
          />
          <button 
            onClick={handleSend} 
            disabled={loading || !input.trim() || interviewEnded} 
            className="send-btn"
          >
            {loading ? (
              <>
                <span className="loading-spinner-small"></span>
                发送中...
              </>
            ) : (
              <>
                <span className="send-icon">📤</span>
                发送
              </>
            )}
          </button>
        </div>
        
        {/* 快捷提示 */}
        {!input.trim() && messageCount === 0 && (
          <div className="quick-tips">
            <span className="tip-text">💡 试试这些开场白：</span>
            <div className="tip-buttons">
              <button 
                onClick={() => setInput("您好，我是...")}
                className="tip-btn"
              >
                自我介绍
              </button>
              <button 
                onClick={() => setInput("我应聘的职位是...")}
                className="tip-btn"
              >
                职位说明
              </button>
            </div>
          </div>
        )}
      </div>
      {/* 语音流播放器控件（仅audio模式下显示） */}
      {mode === "audio" && latestAudioUrl && (
        <div style={{ marginTop: 10 }}>
          <audio src={latestAudioUrl} controls />
        </div>
      )}

    </div>
  );
}
