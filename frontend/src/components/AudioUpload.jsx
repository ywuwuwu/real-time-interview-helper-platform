import React, { useState, useRef } from 'react';

const AudioUpload = ({ 
  onFileSelect, 
  onFileUpload,
  acceptedFormats = ['.mp3', '.wav', '.m4a', '.webm'],
  maxSize = 50, // MB
  className = '',
  disabled = false
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);

  const fileInputRef = useRef(null);
  const audioRef = useRef(null);

  // 验证文件格式
  const validateFileFormat = (file) => {
    const validFormats = acceptedFormats.map(format => format.toLowerCase());
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    return validFormats.includes(fileExtension);
  };

  // 验证文件大小
  const validateFileSize = (file) => {
    const maxSizeInBytes = maxSize * 1024 * 1024; // 转换为字节
    return file.size <= maxSizeInBytes;
  };

  // 处理文件选择
  const handleFileSelect = (file) => {
    if (disabled) return;
    
    setError(null);

    // 验证文件格式
    if (!validateFileFormat(file)) {
      setError(`不支持的文件格式。支持的格式：${acceptedFormats.join(', ')}`);
      return;
    }

    // 验证文件大小
    if (!validateFileSize(file)) {
      setError(`文件大小超过限制。最大允许：${maxSize}MB`);
      return;
    }

    setSelectedFile(file);
    
    // 创建音频预览URL
    const url = URL.createObjectURL(file);
    setAudioUrl(url);
    
    onFileSelect?.(file, url);
  };

  // 处理文件输入
  const handleFileInput = (event) => {
    const file = event.target.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  // 处理拖拽事件
  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragOver(false);

    const files = event.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  // 上传文件
  const uploadFile = async () => {
    if (!selectedFile || disabled) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('audio', selectedFile);
      
      // 这里可以调用上传API
      // const response = await fetch('/api/upload-audio', {
      //   method: 'POST',
      //   body: formData
      // });
      
      // 模拟上传
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      onFileUpload?.(selectedFile, audioUrl);
      
    } catch (err) {
      console.error('上传失败:', err);
      setError('上传失败，请重试');
    } finally {
      setIsUploading(false);
    }
  };

  // 移除文件
  const removeFile = () => {
    setSelectedFile(null);
    setAudioUrl(null);
    setError(null);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // 格式化文件大小
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={`audio-upload ${className}`}>
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

      {!selectedFile ? (
        // 文件选择区域
        <div 
          className={`upload-area ${isDragOver ? 'drag-over' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="upload-content">
            <div className="upload-icon">📁</div>
            <h3>选择音频文件</h3>
            <p>点击或拖拽音频文件到此处</p>
            <div className="upload-info">
              <p>支持的格式：{acceptedFormats.join(', ')}</p>
              <p>最大文件大小：{maxSize}MB</p>
            </div>
            <button 
              className="btn btn-primary select-file-btn"
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
              disabled={disabled}
            >
              <span className="btn-icon">📂</span>
              选择文件
            </button>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept={acceptedFormats.join(',')}
            onChange={handleFileInput}
            style={{ display: 'none' }}
          />
        </div>
      ) : (
        // 文件预览区域
        <div className="file-preview">
          <div className="file-info">
            <div className="file-icon">🎵</div>
            <div className="file-details">
              <h4>{selectedFile.name}</h4>
              <p>大小：{formatFileSize(selectedFile.size)}</p>
              <p>类型：{selectedFile.type || '未知'}</p>
            </div>
          </div>

          {/* 音频播放器 */}
          {audioUrl && (
            <div className="audio-preview">
              <audio 
                ref={audioRef}
                src={audioUrl}
                controls
                className="audio-player"
              />
            </div>
          )}

          {/* 操作按钮 */}
          <div className="file-actions">
            <button 
              className="btn btn-primary upload-file-btn"
              onClick={uploadFile}
              disabled={isUploading || disabled}
            >
              <span className="btn-icon">
                {isUploading ? '⏳' : '📤'}
              </span>
              {isUploading ? '上传中...' : '上传文件'}
            </button>
            
            <button 
              className="btn btn-outline remove-file-btn"
              onClick={removeFile}
            >
              <span className="btn-icon">🗑️</span>
              移除文件
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AudioUpload;
