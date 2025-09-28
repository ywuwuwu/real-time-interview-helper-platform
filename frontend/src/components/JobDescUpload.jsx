import React, { useState } from "react";

function JobDescUpload({ onJDSubmit, onAdvice }) {
  const [fileName, setFileName] = useState("");
  const [jdText, setJdText] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [adviceLoading, setAdviceLoading] = useState(false);

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
      setFile(file);
      setError("");
    }
  }

  function handleTextChange(e) {
    setJdText(e.target.value);
    setError("");
  }

  async function handleReadFile() {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target.result;
        setJdText(text);
        setLoading(false);
      };
      reader.onerror = () => {
        setError("文件读取失败");
        setLoading(false);
      };
      reader.readAsText(file);
    } catch (err) {
      setError("文件读取失败");
      setLoading(false);
    }
  }

  function handleConfirm() {
    if (!jdText.trim()) {
      setError("请粘贴JD文本或上传文件");
      return;
    }
    onJDSubmit(jdText.trim());
  }

  async function handleAdvice() {
    if (!jdText.trim()) {
      setError("请粘贴JD文本或上传文件");
      return;
    }
    setAdviceLoading(true);
    if (onAdvice) onAdvice({ advice: '', loading: true, error: '' });
    try {
      const formData = new FormData();
      formData.append("jd_text", jdText.trim());
      const resp = await fetch("/api/jd_advice", {
        method: "POST",
        body: formData
      });
      const data = await resp.json();
      if (onAdvice) onAdvice({ advice: data.advice || "未收到建议，请检查后端服务。", loading: false, error: '' });
    } catch (err) {
      if (onAdvice) onAdvice({ advice: '', loading: false, error: "请求失败，请稍后重试。" });
    }
    setAdviceLoading(false);
  }

  return (
    <div>
      <label htmlFor="jd-textarea" className="label">
        粘贴职位描述（支持直接从LinkedIn等平台复制）：
      </label>
      <textarea
        id="jd-textarea"
        rows={5}
        value={jdText}
        onChange={handleTextChange}
        placeholder="可直接粘贴JD文本..."
        className="input"
        style={{ width: '100%', marginBottom: 10 }}
      />
      <div style={{ marginBottom: 10, display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <label htmlFor="job-desc-upload" className="label" style={{ marginBottom: 0 }}>
          或上传职位描述文件：
        </label>
        <label className="file-upload">
          <input
            type="file"
            id="job-desc-upload"
            accept=".txt"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          选择文件
        </label>
        {fileName && <span style={{ color: '#2563eb', fontSize: '0.98rem' }}>已选择: {fileName}</span>}
        {file && <button onClick={handleReadFile} className="btn btn-outline" style={{ padding: '2px 10px', fontSize: '0.98rem' }}>读取内容</button>}
      </div>
      <div style={{ display: 'flex', gap: 12 }}>
        <button onClick={handleConfirm} disabled={loading} className="btn btn-primary">
          确认JD并进入面试
        </button>
        <button onClick={handleAdvice} disabled={adviceLoading || loading} className="btn btn-outline">
          {adviceLoading ? '建议生成中...' : '面试建议'}
        </button>
      </div>
      {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
    </div>
  );
}

export default JobDescUpload; 