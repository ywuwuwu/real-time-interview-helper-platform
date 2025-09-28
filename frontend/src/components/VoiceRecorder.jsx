import React, { useState, useRef, useEffect } from 'react';

const VoiceRecorder = ({ 
  onRecordingComplete, 
  onAudioUpload,
  isRecording = false,
  onRecordingChange,
  className = '',
  disabled = false
}) => {
  const [isRecordingState, setIsRecordingState] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);
  const timerRef = useRef(null);

  // 检查浏览器是否支持录音
  const checkRecordingSupport = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (err) {
      setError('浏览器不支持录音功能，请使用Chrome或Firefox浏览器');
      return false;
    }
  };

  // 开始录音
  const startRecording = async () => {
    if (disabled) return;
    
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });

      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        onRecordingComplete?.(blob, url);
      };

      mediaRecorderRef.current.start();
      setIsRecordingState(true);
      onRecordingChange?.(true);
      
      // 开始计时
      setRecordingTime(0);
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (err) {
      console.error('录音失败:', err);
      setError('无法访问麦克风，请检查权限设置');
    }
  };

  // 停止录音
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecordingState) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecordingState(false);
      onRecordingChange?.(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  // 播放录音
  const playRecording = () => {
    if (audioRef.current && audioUrl) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  // 停止播放
  const stopPlaying = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  // 重新录音
  const reRecord = () => {
    setAudioBlob(null);
    setAudioUrl(null);
    setRecordingTime(0);
    setIsPlaying(false);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  };

  // 上传录音
  const uploadRecording = async () => {
    if (!audioBlob) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      
      // 这里可以调用上传API
      // const response = await fetch('/api/upload-audio', {
      //   method: 'POST',
      //   body: formData
      // });
      
      // 模拟上传
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      onAudioUpload?.(audioBlob, audioUrl);
      
    } catch (err) {
      console.error('上传失败:', err);
      setError('上传失败，请重试');
    } finally {
      setIsUploading(false);
    }
  };

  // 格式化时间
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // 组件卸载时清理
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  // 检查录音支持
  useEffect(() => {
    checkRecordingSupport();
  }, []);

  return (
    <div className={`voice-recorder ${className}`}>
      {/* 错误提示 */}
      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
          <button 
            className="error-close"
            onClick={() => setError(null)}
          >
            ×
          </button>
        </div>
      )}

      {/* 录音状态显示 */}
      {isRecordingState && (
        <div className="recording-status">
          <div className="recording-indicator">
            <div className="pulse-dot"></div>
            <span>录音中...</span>
            <span className="recording-time">{formatTime(recordingTime)}</span>
          </div>
        </div>
      )}

      {/* 录音控制按钮 */}
      <div className="recorder-controls">
        {!audioBlob ? (
          // 录音模式
          <div className="recording-mode">
            {!isRecordingState ? (
              <button 
                className="btn btn-primary record-btn"
                onClick={startRecording}
                disabled={!!error || disabled}
              >
                <span className="btn-icon">🎤</span>
                开始录音
              </button>
            ) : (
              <button 
                className="btn btn-danger stop-btn"
                onClick={stopRecording}
              >
                <span className="btn-icon">⏹️</span>
                停止录音
              </button>
            )}
          </div>
        ) : (
          // 播放模式
          <div className="playback-mode">
            <div className="audio-player">
              <audio 
                ref={audioRef}
                src={audioUrl}
                onEnded={() => setIsPlaying(false)}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
              />
              
              <div className="playback-controls">
                {!isPlaying ? (
                  <button 
                    className="btn btn-primary play-btn"
                    onClick={playRecording}
                  >
                    <span className="btn-icon">▶️</span>
                    播放录音
                  </button>
                ) : (
                  <button 
                    className="btn btn-secondary pause-btn"
                    onClick={stopPlaying}
                  >
                    <span className="btn-icon">⏸️</span>
                    暂停播放
                  </button>
                )}
                
                <button 
                  className="btn btn-outline re-record-btn"
                  onClick={reRecord}
                >
                  <span className="btn-icon">🔄</span>
                  重新录音
                </button>
                
                <button 
                  className="btn btn-primary upload-btn"
                  onClick={uploadRecording}
                  disabled={isUploading}
                >
                  <span className="btn-icon">
                    {isUploading ? '⏳' : '📤'}
                  </span>
                  {isUploading ? '上传中...' : '上传录音'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 录音提示 */}
      {!audioBlob && !isRecordingState && (
        <div className="recording-tips">
          <p>💡 录音提示：</p>
          <ul>
            <li>请确保麦克风权限已开启</li>
            <li>建议在安静环境下录音</li>
            <li>录音时长建议控制在2-5分钟</li>
            <li>录音完成后可以播放预览</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;
