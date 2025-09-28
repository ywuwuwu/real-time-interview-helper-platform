import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, Calendar, Lightbulb, Shield, Zap, Target, Check, Star } from 'lucide-react';

const HomePage = () => {
  const navigate = useNavigate();
  
  // 滚动到功能介绍区
  const scrollToFeatures = () => {
    const featuresSection = document.getElementById('features');
    if (featuresSection) {
      featuresSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-white relative overflow-hidden">
      {/* 顶部装饰渐变 */}
      <div className="absolute top-0 left-0 right-0 h-96 bg-gradient-to-br from-indigo-50 via-blue-50 to-purple-50 opacity-60"></div>
      {/* 左上角 LOGO */}
      <div className="absolute top-6 left-6 z-20">
        <img 
          src="/logo.png" 
          alt="Interview Suite Logo" 
          className="h-20 lg:h-24 xl:h-28 object-contain"
        />
      </div>
      
      <div className="absolute top-0 left-0 right-0 h-64 bg-gradient-to-b from-white/80 to-transparent"></div>

      {/* Hero 区域 */}
      <section className="w-full bg-gradient-to-b from-slate-50 to-white py-24 lg:py-32 relative">
        {/* 背景装饰 */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-50/30 via-transparent to-blue-50/20"></div>
        <div className="absolute top-10 left-10 w-32 h-32 bg-indigo-100/40 rounded-full blur-3xl"></div>
        <div className="absolute top-20 right-20 w-40 h-40 bg-blue-100/40 rounded-full blur-3xl"></div>
        
        <div className="container mx-auto max-w-screen-2xl px-6 md:px-8 relative z-10">
          <h1 className="block w-full text-center fluid-h1 font-extrabold tracking-tight text-gray-900">
            让面试准备更高效的 AI 助手
          </h1>
          <p className="mt-6 block w-full text-center text-slate-600 fluid-p max-w-4xl mx-auto">
            从实时面试模拟到个性化培训计划，一站式搞定
          </p>

          {/* CTA 区域：明确居中 */}
          <div className="mt-10 flex flex-col sm:flex-row justify-center gap-4">
            <button 
              onClick={() => navigate('/helper')}
              className="bg-indigo-600 text-white px-10 py-5 rounded-xl text-lg font-semibold hover:bg-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1 hover:scale-105"
            >
              立即开始
            </button>
            <button 
              onClick={scrollToFeatures}
              className="border-2 border-indigo-600 text-indigo-600 px-10 py-5 rounded-xl text-lg font-semibold hover:bg-indigo-50 transition-all duration-300 hover:scale-105"
            >
              了解更多
            </button>
          </div>

          {/* 主页图片 */}
          <div className="mt-16 mx-auto w-full max-w-6xl">
            <img 
              src="/homepage.png" 
              alt="Interview Suite 主页展示图" 
              className="w-full h-auto object-contain"
            />
          </div>
        </div>
      </section>

      {/* 功能入口区 */}
      <section id="features" className="w-full py-24 lg:py-32 bg-white relative">
        {/* 背景装饰 */}
        <div className="absolute inset-0 bg-gradient-to-br from-gray-50/50 via-white to-blue-50/30"></div>
        
        <div className="container mx-auto max-w-screen-2xl px-6 md:px-8 relative z-10">
          <h2 className="block w-full text-center fluid-h2 font-bold text-gray-900">
            选择您的面试工具
          </h2>
          <p className="mt-4 block w-full text-center text-slate-600 fluid-p max-w-3xl mx-auto">
            根据您的需求，选择最适合的面试准备方式
          </p>

          {/* 卡片区域：整体居中并限制宽度 */}
          <div className="mt-12 grid gap-10 lg:gap-12 md:grid-cols-2 max-w-5xl mx-auto">
            {/* Interview Helper 卡片 */}
            <div className="bg-white rounded-3xl shadow-2xl p-8 lg:p-10 hover:shadow-3xl hover:scale-105 transition-all duration-500 cursor-pointer border border-gray-100/50 backdrop-blur-sm">
              <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-br from-indigo-100 to-indigo-200 rounded-2xl mb-8 mx-auto shadow-lg">
                <Mic className="w-10 h-10 text-indigo-600" />
              </div>
              <h3 className="text-2xl lg:text-3xl font-bold text-gray-900 mb-6 text-center">
                Interview Helper
              </h3>
              <p className="text-gray-600 mb-8 text-center text-lg leading-relaxed">
                提供普通面试与考公面试的智能练习，实时反馈帮助您快速提升
              </p>
              <button 
                onClick={() => navigate('/helper')}
                className="w-full bg-gradient-to-r from-indigo-600 to-indigo-700 text-white py-4 rounded-xl font-semibold hover:from-indigo-700 hover:to-indigo-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                进入 Interview Helper
              </button>
            </div>
            
            {/* Interview Planner 卡片 */}
            <div className="bg-white rounded-3xl shadow-2xl p-8 lg:p-10 hover:shadow-3xl hover:scale-105 transition-all duration-500 cursor-pointer border border-gray-100/50 backdrop-blur-sm">
              <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-100 to-green-200 rounded-2xl mb-8 mx-auto shadow-lg">
                <Calendar className="w-10 h-10 text-green-600" />
              </div>
              <h3 className="text-2xl lg:text-3xl font-bold text-gray-900 mb-6 text-center">
                Interview Planner
              </h3>
              <p className="text-gray-600 mb-8 text-center text-lg leading-relaxed">
                上传JD与简历，获取面试培训计划与专业建议，让准备更有针对性
              </p>
              <button 
                onClick={() => navigate('/planner')}
                className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-4 rounded-xl font-semibold hover:from-green-700 hover:to-green-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                进入 Interview Planner
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 产品亮点区 */}
      <section className="w-full py-24 lg:py-32 bg-gradient-to-br from-slate-50 via-blue-50/20 to-indigo-50/30 relative">
        {/* 背景装饰 */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50/80 via-blue-50/40 to-indigo-50/60"></div>
        <div className="absolute top-10 right-10 w-32 h-32 bg-blue-100/30 rounded-full blur-3xl"></div>
        <div className="absolute bottom-10 left-10 w-40 h-40 bg-indigo-100/30 rounded-full blur-3xl"></div>
        
        <div className="container mx-auto max-w-screen-2xl px-6 md:px-8 relative z-10">
          <h2 className="block w-full text-center fluid-h2 font-bold text-gray-900">
            为什么选择 Interview Suite
          </h2>
          <p className="mt-4 block w-full text-center text-slate-600 fluid-p max-w-3xl mx-auto">
            AI 驱动的面试准备平台，助您在竞争中脱颖而出
          </p>

          <div className="mt-12 grid gap-10 lg:gap-12 md:grid-cols-2 lg:grid-cols-4">
            {/* 亮点 1 */}
            <div className="text-center">
              <div className="flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4 mx-auto">
                <Lightbulb className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">智能分析</h3>
              <p className="text-gray-600">
                AI 深度分析您的回答，提供精准的改进建议
              </p>
            </div>
            
            {/* 亮点 2 */}
            <div className="text-center">
              <div className="flex items-center justify-center w-16 h-16 bg-purple-100 rounded-full mb-4 mx-auto">
                <Shield className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">专业可靠</h3>
              <p className="text-gray-600">
                基于真实面试场景，覆盖各行业常见面试题型
              </p>
            </div>
            
            {/* 亮点 3 */}
            <div className="text-center">
              <div className="flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4 mx-auto">
                <Zap className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">快速提升</h3>
              <p className="text-gray-600">
                个性化练习计划，帮您在最短时间内显著提升
              </p>
            </div>
            
            {/* 亮点 4 */}
            <div className="text-center">
              <div className="flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4 mx-auto">
                <Target className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">精准匹配</h3>
              <p className="text-gray-600">
                根据职位要求定制面试内容，针对性强
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 工作流程区 */}
      <section className="w-full py-24 lg:py-32 bg-white relative">
        {/* 背景装饰 */}
        <div className="absolute inset-0 bg-gradient-to-br from-white via-gray-50/30 to-slate-50/50"></div>
        
        <div className="container mx-auto max-w-screen-2xl px-6 md:px-8 relative z-10">
          <h2 className="block w-full text-center fluid-h2 font-bold text-gray-900">
            三步开启您的面试之旅
          </h2>
          <p className="mt-4 block w-full text-center text-slate-600 fluid-p max-w-3xl mx-auto">
            简单几步，即可开始专业的面试练习
          </p>

          <div className="mt-12 grid gap-10 lg:gap-12 md:grid-cols-3">
            {/* 步骤 1 */}
            <div className="bg-white rounded-3xl shadow-2xl p-8 lg:p-10 text-center border border-gray-100/50 backdrop-blur-sm hover:shadow-3xl transition-all duration-500">
              <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-100 to-indigo-200 rounded-2xl mb-8 mx-auto text-indigo-600 font-bold text-2xl shadow-lg">
                1
              </div>
              <h3 className="text-xl lg:text-2xl font-semibold text-gray-900 mb-6">
                选择面试类型 / 上传JD
              </h3>
              <p className="text-gray-600 text-lg leading-relaxed">
                选择您要练习的面试类型，或上传具体的职位描述，让AI了解您的需求
              </p>
            </div>
            
            {/* 步骤 2 */}
            <div className="bg-white rounded-3xl shadow-2xl p-8 lg:p-10 text-center border border-gray-100/50 backdrop-blur-sm hover:shadow-3xl transition-all duration-500">
              <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-green-100 to-green-200 rounded-2xl mb-8 mx-auto text-green-600 font-bold text-2xl shadow-lg">
                2
              </div>
              <h3 className="text-xl lg:text-2xl font-semibold text-gray-900 mb-6">
                AI 实时问答与分析
              </h3>
              <p className="text-gray-600 text-lg leading-relaxed">
                与AI面试官进行真实的面试对话，获得实时的表现分析和反馈
              </p>
            </div>
            
            {/* 步骤 3 */}
            <div className="bg-white rounded-3xl shadow-2xl p-8 lg:p-10 text-center border border-gray-100/50 backdrop-blur-sm hover:shadow-3xl transition-all duration-500">
              <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-100 to-blue-200 rounded-2xl mb-8 mx-auto text-blue-600 font-bold text-2xl shadow-lg">
                3
              </div>
              <h3 className="text-xl lg:text-2xl font-semibold text-gray-900 mb-6">
                获得改进建议 & 培训计划
              </h3>
              <p className="text-gray-600 text-lg leading-relaxed">
                收到详细的表现报告和个性化的培训计划，持续提升面试技能
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 页脚 */}
      <footer className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white py-16 relative overflow-hidden">
        {/* 底部装饰渐变 */}
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900/90 via-gray-800/80 to-gray-900/90"></div>
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-indigo-900/20 to-transparent"></div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid md:grid-cols-3 gap-8">
            {/* 公司信息 */}
            <div>
              <h3 className="text-xl font-bold mb-4">Interview Suite</h3>
              <p className="text-gray-400 mb-4">
                专业的AI面试准备平台，帮助求职者在面试中获得成功。
              </p>
            </div>
            
            {/* 联系方式 */}
            <div>
              <h3 className="text-xl font-bold mb-4">联系我们</h3>
              <div className="space-y-2 text-gray-400">
                <p>邮箱：</p>
                <p>电话：</p>
                <p>地址：</p>
              </div>
            </div>
            
            {/* 产品链接 */}
            <div>
              <h3 className="text-xl font-bold mb-4">产品</h3>
              <div className="space-y-2 text-gray-400">
                <p><button className="hover:text-white transition-colors">Interview Helper</button></p>
                <p><button className="hover:text-white transition-colors">Interview Planner</button></p>
                <p><button className="hover:text-white transition-colors">使用指南</button></p>
              </div>
            </div>
          </div>
          
          {/* 版权信息 */}
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Interview Suite. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
