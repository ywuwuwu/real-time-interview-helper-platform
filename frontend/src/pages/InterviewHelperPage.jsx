import React from 'react';
import { useNavigate } from 'react-router-dom';
import InterviewHelper from '../App.jsx';

const InterviewHelperPage = () => {
  const navigate = useNavigate();

  const handleBackToHome = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* 左侧返回按钮 */}
            <button 
              onClick={handleBackToHome}
              className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              返回首页
            </button>
            
            {/* 中间标题 */}
            <div className="flex-1 flex justify-center">
              <h1 className="text-2xl font-bold text-indigo-600">Interview Helper</h1>
            </div>
            
            {/* 右侧空白保持平衡 */}
            <div className="w-24"></div>
          </div>
        </div>
      </nav>

      {/* Interview Helper 内容 */}
      <InterviewHelper />
    </div>
  );
};

export default InterviewHelperPage;
