import React, { useState } from 'react';
import CivilServiceSelector from './CivilServiceSelector';
import CivilServiceInterview from './CivilServiceInterview';

const TestCivilService = () => {
  const [currentView, setCurrentView] = useState('selector'); // 'selector' or 'interview'
  const [examConfig, setExamConfig] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [improvements, setImprovements] = useState([]);

  const handleConfigSelect = (config) => {
    setExamConfig(config);
    setCurrentView('interview');
  };

  const handleFeedback = (newFeedback) => {
    setFeedback(newFeedback);
    console.log('收到反馈:', newFeedback);
  };

  const handleImprovements = (newImprovements) => {
    setImprovements(newImprovements);
    console.log('收到改进建议:', newImprovements);
  };

  const resetTest = () => {
    setCurrentView('selector');
    setExamConfig(null);
    setFeedback(null);
    setImprovements([]);
  };

  return (
    <div className="test-civil-service">
      <div className="test-header">
        <h2>🏛️ 考公面试功能测试</h2>
        <div className="test-controls">
          <button 
            onClick={resetTest}
            className="btn btn-outline"
          >
            重置测试
          </button>
        </div>
      </div>

      <div className="test-status">
        <h3>测试状态</h3>
        <div className="status-grid">
          <div className="status-item">
            <span className="label">当前视图：</span>
            <span className="value">{currentView}</span>
          </div>
          <div className="status-item">
            <span className="label">考试配置：</span>
            <span className="value">
              {examConfig ? `${examConfig.examName}` : '未设置'}
            </span>
          </div>
          <div className="status-item">
            <span className="label">反馈状态：</span>
            <span className="value">
              {feedback ? '已收到' : '未收到'}
            </span>
          </div>
          <div className="status-item">
            <span className="label">改进建议：</span>
            <span className="value">
              {improvements.length > 0 ? `${improvements.length}条` : '无'}
            </span>
          </div>
        </div>
      </div>

      <div className="test-content">
        {currentView === 'selector' ? (
          <CivilServiceSelector 
            onSelect={handleConfigSelect}
            selectedConfig={examConfig}
          />
        ) : (
          <CivilServiceInterview 
            examConfig={examConfig}
            onFeedback={handleFeedback}
            onImprovements={handleImprovements}
            interviewEnded={false}
          />
        )}
      </div>

      {feedback && (
        <div className="test-results">
          <h3>📊 测试结果</h3>
          <div className="results-content">
            <div className="result-item">
              <h4>反馈内容</h4>
              <pre>{JSON.stringify(feedback, null, 2)}</pre>
            </div>
            <div className="result-item">
              <h4>改进建议</h4>
              <ul>
                {improvements.map((improvement, index) => (
                  <li key={index}>{improvement}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestCivilService; 