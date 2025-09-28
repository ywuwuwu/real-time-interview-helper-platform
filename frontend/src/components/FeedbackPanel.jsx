import React, { useState } from "react";
import { fetchTTS} from "../api";

function FeedbackPanel({ feedback, improvements }) {
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);

  async function handlePlay() {
    if (!feedback) return;
    setLoading(true);
    try {
      const text = Object.values(feedback).join("。");
      const blob = await fetchTTS(text);
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
      const audio = new Audio(url);
      audio.play();
    } catch (e) {
      alert("获取语音失败");
    }
    setLoading(false);
  }

  if (!feedback && (!improvements || improvements.length === 0)) {
    return null;
  }

  return (
    <div className="section-card" style={{ border: '1px solid #e0e7ef', marginTop: '1rem', background: '#f8fafc' }}>
      <div style={{ fontWeight: 600, marginBottom: 6 }}>面试反馈：</div>
      {feedback && (
        <div style={{ marginBottom: 8 }}>
          {Object.entries(feedback).map(([k, v]) => (
            <div key={k}><strong>{k}：</strong>{v}</div>
          ))}
        </div>
      )}
      {improvements && improvements.length > 0 && (
        <div>
          <strong>改进建议：</strong>
          <ul style={{ margin: '6px 0 0 18px' }}>
            {improvements.map((item, idx) => <li key={idx}>{item}</li>)}
          </ul>
        </div>
      )}
      {feedback && (
        <button
          onClick={handlePlay}
          disabled={loading}
          className="btn btn-primary"
          style={{ marginTop: 12 }}
        >
          {loading ? "生成语音中..." : "语音播报"}
        </button>
      )}
      {audioUrl && <audio src={audioUrl} controls autoPlay style={{ display: "block", marginTop: 6 }} />}
    </div>
  );
}

export default FeedbackPanel; 