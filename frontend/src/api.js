import React from "react";

export async function transcribeAudio(audioBlob) {
  const formData = new FormData();
  formData.append('file', audioBlob, 'audio.wav');
  const response = await fetch('/api/transcribe', {
    method: 'POST',
    body: formData,
  });
  const data = await response.json();
  return { text: data.transcript }; // 适配为原有格式
}

// 其他 API 方法可在此扩展 

// api.js

// 1. /api/tts
export async function fetchTTS(text, voice = "alloy", speed = 1.0) {
  const res = await fetch("/api/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, voice, speed }),
  });
  const audioBlob = await res.blob();
  return audioBlob;
}

// 2. /api/rag-tts
export async function fetchRagTTS(userInput, jobTitle, jobDesc, voice = "alloy", ttsModel = "tts-1") {
  const res = await fetch("/api/rag-tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_input: userInput,
      job_title: jobTitle,
      job_desc: jobDesc,
      voice,
      tts_model: ttsModel,
    }),
  });
  const audioBlob = await res.blob();
  // 可从header取出AI文字答案
  const ragText = decodeURIComponent(res.headers.get("X-RAG-Text") || "");
  let feedback = null, improvements = [];
  try {
    feedback = JSON.parse(decodeURIComponent(res.headers.get("X-RAG-Feedback") || "null"));
    improvements = JSON.parse(decodeURIComponent(res.headers.get("X-RAG-Improvements") || "[]"));
  } catch {}
  return { audioBlob, ragText, feedback, improvements };
}

// api.js
export async function fetchRagTTSMultipart(userInput, jobTitle, jobDesc, voice = "alloy", ttsModel = "tts-1") {
  const res = await fetch("/api/rag-tts-multipart", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_input: userInput,
      job_title: jobTitle,
      job_desc: jobDesc,
      voice,
      tts_model: ttsModel,
    }),
  });
  const contentType = res.headers.get("content-type") || "";
  const boundaryMatch = contentType.match(/boundary=(.*)$/);
  if (!boundaryMatch) throw new Error("未获取到boundary");

  const boundary = boundaryMatch[1];
  const raw = await res.arrayBuffer();
  // 解析multipart
  const parts = splitMultipart(new Uint8Array(raw), boundary);

  // part1: json结构化文本，part2: audio/mpeg
  const jsonStr = new TextDecoder("utf-8").decode(parts[0]);
  const info = JSON.parse(jsonStr);
  const audioBlob = new Blob([parts[1]], { type: "audio/mpeg" });
  return { info, audioBlob };
}

// 解析multipart辅助函数（只处理2段，安全够用）
function splitMultipart(u8arr, boundary) {
  // boundary以--起始
  const sep = new TextEncoder().encode(`--${boundary}`);
  let idx = 0, parts = [];
  while (idx < u8arr.length) {
    // 找boundary起点
    let start = indexOfArr(u8arr, sep, idx);
    if (start < 0) break;
    start += sep.length;
    // 跳到下一个header后
    let headerEnd = indexOfArr(u8arr, new Uint8Array([13,10,13,10]), start); // \r\n\r\n
    if (headerEnd < 0) break;
    headerEnd += 4;
    let next = indexOfArr(u8arr, sep, headerEnd);
    if (next < 0) next = u8arr.length;
    parts.push(u8arr.slice(headerEnd, next-2)); // -2 去掉前面的 \r\n
    idx = next;
  }
  return parts;
}
function indexOfArr(haystack, needle, fromIdx=0) {
  for (let i=fromIdx; i<haystack.length-needle.length+1; ++i) {
    let ok = true;
    for (let j=0; j<needle.length; ++j)
      if (haystack[i+j] !== needle[j]) { ok = false; break; }
    if (ok) return i;
  }
  return -1;
}


// api.js

// 面试对话WebSocket hook
export function useInterviewWebSocket({
  onText,     // (data: {ai_response, feedback, ...}) => void
  onAudio,    // (audioChunk: ArrayBuffer) => void
  onOpen,     // () => void
  onClose,    // () => void
  onError,    // (err) => void
}) {
  const wsRef = React.useRef(null);

  // 连接WebSocket
  function connect() {
    const ws = new WebSocket("ws://localhost:8000/ws/interview"); // 按实际端口
    ws.binaryType = "arraybuffer"; // 音频流需要设置

    ws.onopen = () => {
      if (onOpen) onOpen(ws);   // 传递 ws 对象
    };
    ws.onclose = () => { if (onClose) onClose(); };
    ws.onerror = (e) => { if (onError) onError(e); };

    ws.onmessage = (evt) => {
      // 音频流是二进制，结构化数据是string
      if (typeof evt.data === "string") {
        try {
          const data = JSON.parse(evt.data);
          if (onText) onText(data);
        } catch {
          // 非JSON字符串
        }
      } else if (evt.data instanceof ArrayBuffer) {
        if (onAudio) onAudio(evt.data);
      }
    };

    wsRef.current = ws;
  }

  // 发送一轮问答
  function sendUserInput({ user_input, job_title, job_desc, voice, tts_model, session_id }) {
    if (!wsRef.current) {
      console.log("[sendUserInput] wsRef.current is null!");
      return;
    }
    if (wsRef.current.readyState !== 1) {
      console.log("[sendUserInput] ws not open, readyState=", wsRef.current.readyState);
      return;
    }
    const payload = { user_input, job_title, job_desc, voice, tts_model, session_id };
    console.log("[sendUserInput] Sending:", payload);
    wsRef.current.send(JSON.stringify(payload));
    
    // if (!wsRef.current || wsRef.current.readyState !== 1) return;
    // wsRef.current.send(JSON.stringify({
    //   user_input, job_title, job_desc, voice, tts_model, session_id
    // }));
  }

  // 关闭
  function close() {
    if (wsRef.current) wsRef.current.close();
  }

  // 断线重连（可选）
  function reconnect() {
    close();
    setTimeout(connect, 1000);
  }

  // 组件销毁时自动断开
  React.useEffect(() => {
    return () => { close(); };
  }, []);

  return {
    connect,
    sendUserInput,
    close,
    reconnect,
  };
}

// ===== Interview Planner API Methods =====

// 创建面试规划
export async function createInterviewPlan(planData) {
  const response = await fetch("/api/planner/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(planData),
  });
  
  if (!response.ok) {
    throw new Error(`创建规划失败: ${response.statusText}`);
  }
  
  return await response.json();
}

// 获取面试规划详情
export async function getInterviewPlan(planId) {
  const response = await fetch(`/api/planner/${planId}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  
  if (!response.ok) {
    throw new Error(`获取规划失败: ${response.statusText}`);
  }
  
  return await response.json();
}

// 更新学习进度
export async function updateProgress(planId, progressData) {
  const response = await fetch(`/api/planner/${planId}/progress`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(progressData),
  });
  
  if (!response.ok) {
    throw new Error(`更新进度失败: ${response.statusText}`);
  }
  
  return await response.json();
}

// 上传简历
export async function uploadResume(planId, file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`/api/planner/${planId}/upload-resume`, {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error(`上传简历失败: ${response.statusText}`);
  }
  
  return await response.json();
}

// 获取用户规划总结
export async function getUserPlannerSummary(userId) {
  const response = await fetch(`/api/planner/user/${userId}/summary`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  
  if (!response.ok) {
    throw new Error(`获取总结失败: ${response.statusText}`);
  }
  
  return await response.json();
}
