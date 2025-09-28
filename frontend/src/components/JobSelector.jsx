import React, { useState } from "react";
import "./JobSelector.css";

const JobSelector = ({ onSelect, selectedJob = "", className = "" }) => {
  const [activeCategory, setActiveCategory] = useState("技术类");
  const [searchTerm, setSearchTerm] = useState("");

  // 职位数据
  const jobCategories = {
    "技术类": [
      { value: "frontend", label: "前端工程师", icon: "💻", description: "负责用户界面开发" },
      { value: "backend", label: "后端工程师", icon: "⚙️", description: "负责服务器端开发" },
      { value: "fullstack", label: "全栈工程师", icon: "🔄", description: "前后端全栈开发" },
      { value: "mobile", label: "移动端工程师", icon: "📱", description: "移动应用开发" },
      { value: "devops", label: "DevOps工程师", icon: "🐳", description: "运维自动化" },
      { value: "data", label: "数据工程师", icon: "📊", description: "数据处理与分析" },
      { value: "ai", label: "AI工程师", icon: "🤖", description: "人工智能开发" },
      { value: "qa", label: "测试工程师", icon: "🔍", description: "软件测试与质量保证" }
    ],
    "产品类": [
      { value: "pm", label: "产品经理", icon: "📋", description: "产品规划与管理" },
      { value: "po", label: "产品运营", icon: "📈", description: "产品运营与推广" },
      { value: "ux", label: "UX设计师", icon: "🎨", description: "用户体验设计" },
      { value: "ui", label: "UI设计师", icon: "🎨", description: "用户界面设计" }
    ],
    "考公类": [
      { value: "公务员", label: "公务员", icon: "🏛️", description: "政府机关工作" },
      { value: "事业编", label: "事业编制", icon: "📚", description: "事业单位工作" },
      { value: "教师", label: "教师", icon: "👨‍🏫", description: "教育行业工作" },
      { value: "警察", label: "警察", icon: "👮", description: "公安系统工作" }
    ],
    "其他": [
      { value: "marketing", label: "市场营销", icon: "📢", description: "市场推广与营销" },
      { value: "sales", label: "销售", icon: "💰", description: "产品销售" },
      { value: "hr", label: "人力资源", icon: "👥", description: "人力资源管理" },
      { value: "finance", label: "财务", icon: "💼", description: "财务管理" }
    ]
  };

  // 获取选中职位的显示信息
  const getSelectedJobInfo = () => {
    const allJobs = Object.values(jobCategories).flat();
    return allJobs.find(job => job.value === selectedJob) || null;
  };

  const selectedJobInfo = getSelectedJobInfo();

  const handleJobSelect = (jobValue) => {
    onSelect && onSelect(jobValue);
  };

  const handleClear = () => {
    onSelect && onSelect("");
    setSearchTerm("");
  };

  // 过滤职位
  const getFilteredJobs = () => {
    if (!searchTerm) return jobCategories[activeCategory] || [];
    
    const allJobs = Object.values(jobCategories).flat();
    return allJobs.filter(job => 
      job.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.description.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  const filteredJobs = getFilteredJobs();
  const isSearchMode = searchTerm.length > 0;

  return (
    <div className={`job-selector ${className}`}>
      <div className="selector-container">
        {/* 已选择的职位显示 */}
        {selectedJobInfo && (
          <div className="selected-job-display">
            <div className="selected-job-card">
              <span className="job-icon">{selectedJobInfo.icon}</span>
              <div className="job-info">
                <span className="job-label">{selectedJobInfo.label}</span>
                <span className="job-description">{selectedJobInfo.description}</span>
              </div>
              <button className="clear-selection-btn" onClick={handleClear}>
                <span className="btn-icon">✕</span>
              </button>
            </div>
          </div>
        )}

        {/* 搜索框 */}
        <div className="search-section">
          <label className="label">
            选择职位：
          </label>
          <div className="search-input-wrapper">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="搜索职位或描述..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            {searchTerm && (
              <button 
                className="clear-search-btn"
                onClick={() => setSearchTerm("")}
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* 分类标签 */}
        {!isSearchMode && (
          <div className="category-tabs">
            {Object.keys(jobCategories).map((category) => (
              <button
                key={category}
                className={`category-tab ${activeCategory === category ? 'active' : ''}`}
                onClick={() => setActiveCategory(category)}
              >
                {category}
              </button>
            ))}
          </div>
        )}

        {/* 职位网格 */}
        <div className="jobs-grid">
          {isSearchMode ? (
            // 搜索模式：显示所有匹配的职位
            filteredJobs.map((job) => (
              <div
                key={job.value}
                className={`job-card ${selectedJob === job.value ? 'selected' : ''}`}
                onClick={() => handleJobSelect(job.value)}
              >
                <div className="job-card-icon">{job.icon}</div>
                <div className="job-card-content">
                  <h4 className="job-card-title">{job.label}</h4>
                  <p className="job-card-description">{job.description}</p>
                </div>
                {selectedJob === job.value && (
                  <div className="selection-indicator">
                    <span className="check-icon">✓</span>
                  </div>
                )}
              </div>
            ))
          ) : (
            // 分类模式：显示当前分类的职位
            (jobCategories[activeCategory] || []).map((job) => (
              <div
                key={job.value}
                className={`job-card ${selectedJob === job.value ? 'selected' : ''}`}
                onClick={() => handleJobSelect(job.value)}
              >
                <div className="job-card-icon">{job.icon}</div>
                <div className="job-card-content">
                  <h4 className="job-card-title">{job.label}</h4>
                  <p className="job-card-description">{job.description}</p>
                </div>
                {selectedJob === job.value && (
                  <div className="selection-indicator">
                    <span className="check-icon">✓</span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* 无搜索结果提示 */}
        {isSearchMode && filteredJobs.length === 0 && (
          <div className="no-results">
            <div className="no-results-icon">🔍</div>
            <p>未找到匹配的职位</p>
            <button 
              className="clear-search-btn-large"
              onClick={() => setSearchTerm("")}
            >
              清除搜索
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobSelector;