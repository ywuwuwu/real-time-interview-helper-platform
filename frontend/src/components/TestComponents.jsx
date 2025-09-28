import React, { useState } from 'react';
import JobSelector from './JobSelector';
import VoiceRecorder from './VoiceRecorder';
import AudioUpload from './AudioUpload';
import TestCivilService from './TestCivilService';

const TestComponents = () => {
  const [selectedJob, setSelectedJob] = useState('');
  const [testResults, setTestResults] = useState([]);
  const [activeTest, setActiveTest] = useState('basic'); // 'basic' or 'civil-service'

  const addTestResult = (component, action, data) => {
    setTestResults(prev => [...prev, {
      id: Date.now(),
      component,
      action,
      data,
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  return (
    <div className="test-components">
      <div className="test-header">
        <h1>🧪 组件功能测试</h1>
        <p>测试所有新开发的组件功能</p>
        <div className="test-controls">
          <button 
            onClick={() => setActiveTest('basic')}
            className={`btn ${activeTest === 'basic' ? 'btn-primary' : 'btn-outline'}`}
          >
            基础功能测试
          </button>
          <button 
            onClick={() => setActiveTest('civil-service')}
            className={`btn ${activeTest === 'civil-service' ? 'btn-primary' : 'btn-outline'}`}
          >
            考公面试测试
          </button>
        </div>
      </div>

      {activeTest === 'basic' ? (
        <div className="test-grid">
          {/* JobSelector 测试 */}
          <div className="test-section">
            <h2>📋 JobSelector 测试</h2>
            <JobSelector 
              onSelect={(job) => {
                setSelectedJob(job);
                addTestResult('JobSelector', '选择职位', job);
              }}
              selectedJob={selectedJob}
            />
            <div className="test-info">
              <p><strong>当前选择:</strong> {selectedJob || '未选择'}</p>
            </div>
          </div>

          {/* VoiceRecorder 测试 */}
          <div className="test-section">
            <h2>🎙️ VoiceRecorder 测试</h2>
            <VoiceRecorder 
              onRecordingComplete={(blob, url) => {
                addTestResult('VoiceRecorder', '录音完成', {
                  size: blob.size,
                  type: blob.type,
                  url: url
                });
              }}
              onAudioUpload={(blob, url) => {
                addTestResult('VoiceRecorder', '录音上传', {
                  size: blob.size,
                  type: blob.type,
                  url: url
                });
              }}
            />
          </div>

          {/* AudioUpload 测试 */}
          <div className="test-section">
            <h2>📁 AudioUpload 测试</h2>
            <AudioUpload 
              onFileSelect={(file, url) => {
                addTestResult('AudioUpload', '文件选择', {
                  name: file.name,
                  size: file.size,
                  type: file.type,
                  url: url
                });
              }}
              onFileUpload={(file, url) => {
                addTestResult('AudioUpload', '文件上传', {
                  name: file.name,
                  size: file.size,
                  type: file.type,
                  url: url
                });
              }}
            />
          </div>
        </div>
      ) : (
        <TestCivilService />
      )}

      {/* 测试结果 */}
      <div className="test-results">
        <h2>📊 测试结果</h2>
        <div className="results-list">
          {testResults.length === 0 ? (
            <p className="no-results">暂无测试结果</p>
          ) : (
            testResults.map(result => (
              <div key={result.id} className="result-item">
                <div className="result-header">
                  <span className="component-name">{result.component}</span>
                  <span className="action-name">{result.action}</span>
                  <span className="timestamp">{result.timestamp}</span>
                </div>
                <div className="result-data">
                  <pre>{JSON.stringify(result.data, null, 2)}</pre>
                </div>
              </div>
            ))
          )}
        </div>
        
        {testResults.length > 0 && (
          <button 
            className="btn btn-secondary"
            onClick={() => setTestResults([])}
          >
            清除测试结果
          </button>
        )}
      </div>
    </div>
  );
};

export default TestComponents; 