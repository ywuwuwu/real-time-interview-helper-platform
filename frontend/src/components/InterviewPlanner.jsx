import React, { useState } from 'react';
import { 
  createInterviewPlan, 
  getInterviewPlan, 
  updateProgress, 
  uploadResume 
} from '../api';
import './InterviewPlanner.css';

const InterviewPlanner = ({ onBackToInterview }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [planId, setPlanId] = useState(null);
  const [planData, setPlanData] = useState(null);
  const [formData, setFormData] = useState({
    jd: '',
    resume: null,
    questionnaire: {
      experience: '',
      skills: '',
      goals: ''
    },
    progress: {
      courses: 0,
      projects: 0,
      interviews: 0
    }
  });

  const handleFileUpload = (e, type) => {
    const file = e.target.files[0];
    setFormData(prev => ({
      ...prev,
      [type]: file
    }));
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleQuestionnaireChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      questionnaire: {
        ...prev.questionnaire,
        [field]: value
      }
    }));
  };

  const nextStep = async () => {
    if (currentStep === 1) {
      // 第一步：创建面试规划
      await createPlan();
    } else if (currentStep === 2) {
      // 第二步：上传简历
      await uploadResumeFile();
    } else if (currentStep < 5) {
      setCurrentStep(currentStep + 1);
    }
  };

  const createPlan = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const planRequest = {
        job_title: "目标职位", // 可以从formData中获取
        job_description: formData.jd,
        target_company: null,
        experience_years: parseInt(formData.questionnaire.experience) || 0,
        skills: formData.questionnaire.skills.split(',').map(s => s.trim()).filter(s => s),
        career_goals: formData.questionnaire.goals
      };
      
      const result = await createInterviewPlan(planRequest);
      setPlanId(result.id);
      setPlanData(result);
      setCurrentStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const uploadResumeFile = async () => {
    if (!planId || !formData.resume) {
      setCurrentStep(3);
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // 上传简历
      const uploadResult = await uploadResume(planId, formData.resume);
      console.log("简历上传结果:", uploadResult);
      
      // 重新获取更新后的计划数据
      const updatedPlan = await getInterviewPlan(planId);
      console.log("更新后的计划数据:", updatedPlan);
      
      // 更新前端状态
      setPlanData(updatedPlan);
      
      setCurrentStep(3);
    } catch (err) {
      console.error("简历上传失败:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateActivityProgress = async (activityType, activityId, activityName, progress, completed = false) => {
    if (!planId) return;
    
    try {
      await updateProgress(planId, {
        activity_type: activityType,
        activity_id: activityId,
        activity_name: activityName,
        progress_percentage: progress,
        completed: completed
      });
    } catch (err) {
      console.error('更新进度失败:', err);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStep1 = () => (
    <div className="planner-step">
      <div className="step-header">
        <div className="step-icon">📋</div>
        <div className="step-title-section">
          <h3>上传目标JD</h3>
          <p>导入LinkedIn/公司官网招聘信息，开始你的面试规划之旅</p>
        </div>
      </div>
      
      <div className="input-group">
        <label>职位描述 (JD):</label>
        <textarea
          placeholder="请粘贴或输入目标职位描述..."
          value={formData.jd}
          onChange={(e) => handleInputChange('jd', e.target.value)}
          rows={8}
        />
      </div>
      
      <div className="input-group">
        <label>或上传JD文件:</label>
        <input
          type="file"
          accept=".txt,.doc,.docx,.pdf"
          onChange={(e) => handleFileUpload(e, 'jdFile')}
        />
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="planner-step">
      <div className="step-header">
        <div className="step-icon">👤</div>
        <div className="step-title-section">
          <h3>提交用户画像</h3>
          <p>上传简历并完成个人能力评估问卷</p>
        </div>
      </div>
      
      <div className="input-group">
        <label>上传简历:</label>
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={(e) => handleFileUpload(e, 'resume')}
        />
      </div>
      
      <div className="questionnaire">
        <h4>补充问卷</h4>
        
        <div className="input-group">
          <label>工作经验 (年):</label>
          <input
            type="number"
            placeholder="例如: 3"
            value={formData.questionnaire.experience}
            onChange={(e) => handleQuestionnaireChange('experience', e.target.value)}
          />
        </div>
        
        <div className="input-group">
          <label>核心技能 (用逗号分隔):</label>
          <input
            type="text"
            placeholder="例如: Python, React, 项目管理"
            value={formData.questionnaire.skills}
            onChange={(e) => handleQuestionnaireChange('skills', e.target.value)}
          />
        </div>
        
        <div className="input-group">
          <label>职业目标:</label>
          <textarea
            placeholder="描述你的职业发展目标..."
            value={formData.questionnaire.goals}
            onChange={(e) => handleQuestionnaireChange('goals', e.target.value)}
            rows={4}
          />
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => {
    if (!planData) return <div className="loading">正在分析你的技能匹配度...</div>;
    
    return (
      <div className="planner-step">
        <div className="step-header">
          <div className="step-icon">🎯</div>
          <div className="step-title-section">
            <h3>语义匹配 & 差距提炼</h3>
            <p>AI深度分析JD与个人能力的匹配度，识别技能差距</p>
          </div>
        </div>
        
        {/* 简历上传状态 */}
        {planData.resume_path && (
          <div className="resume-status">
            <h4>📄 简历上传状态</h4>
            <div className="status-item">
              <span className="status-icon">✅</span>
              <span>简历已成功上传</span>
            </div>
            <div className="status-item">
              <span className="status-icon">🔍</span>
              <span>已解析技能: {planData.skills?.join(', ') || '无'}</span>
            </div>
            <div className="status-item">
              <span className="status-icon">⏰</span>
              <span>工作经验: {planData.experience_years || 0} 年</span>
            </div>
          </div>
        )}
        
        {/* 匹配度计算过程 */}
        <div className="calculation-process">
          <h4>📊 匹配度计算过程</h4>
          <div className="calculation-item">
            <span className="calculation-label">技能匹配度计算:</span>
            <span className="calculation-value">
              {planData.gap_analysis?.strengths?.length || 0} 个匹配技能 / {planData.gap_analysis?.gaps?.length + (planData.gap_analysis?.strengths?.length || 0) || 0} 个总技能 = {planData.skill_match_score || 0}%
            </span>
          </div>
          <div className="calculation-item">
            <span className="calculation-label">经验匹配度计算:</span>
            <span className="calculation-value">
              用户经验 {planData.experience_years || 0} 年 vs 要求经验 {planData.gap_analysis?.jd_requirements?.experience_requirements?.[0]?.years || 3} 年 = {planData.experience_match_score || 0}%
            </span>
          </div>
        </div>
        
        {/* 详细技能分析 */}
        <div className="detailed-skill-analysis">
          <h4>🔍 详细技能分析</h4>
          
          {/* 我的技能 */}
          <div className="skill-section">
            <h5>✅ 我的技能 ({planData.skills?.length || 0} 项)</h5>
            <div className="skill-list">
              {planData.skills?.map((skill, index) => (
                <span key={index} className="skill-tag my-skill">
                  {skill}
                </span>
              )) || []}
            </div>
          </div>
          
          {/* 匹配的技能 */}
          <div className="skill-section">
            <h5>🎯 匹配的技能 ({planData.gap_analysis?.strengths?.length || 0} 项)</h5>
            <div className="skill-list">
              {planData.gap_analysis?.strengths?.map((strength, index) => (
                <span key={index} className="skill-tag matched-skill">
                  {strength.skill} (重要性: {strength.importance})
                </span>
              )) || []}
            </div>
          </div>
          
          {/* 岗位没有要求的技能 */}
          <div className="skill-section">
            <h5>💡 岗位没有要求的技能</h5>
            <div className="skill-list">
              {planData.skills?.filter(skill => 
                !planData.gap_analysis?.strengths?.some(strength => 
                  strength.skill.toLowerCase() === skill.toLowerCase()
                ) && 
                !planData.gap_analysis?.gaps?.some(gap => 
                  gap.skill.toLowerCase() === skill.toLowerCase()
                )
              ).map((skill, index) => (
                <span key={index} className="skill-tag extra-skill">
                  {skill}
                </span>
              )) || []}
            </div>
          </div>
          
          {/* 岗位要求但我没有的技能 */}
          <div className="skill-section">
            <h5>❌ 岗位要求但我没有的技能 ({planData.gap_analysis?.gaps?.length || 0} 项)</h5>
            <div className="skill-list">
              {planData.gap_analysis?.gaps?.map((gap, index) => (
                <span key={index} className={`skill-tag missing-skill ${gap.priority}`}>
                  {gap.skill} ({gap.priority} priority)
                  {gap.similar_skill && <small> - 相关技能: {gap.similar_skill}</small>}
                </span>
              )) || []}
            </div>
          </div>
        </div>
        
        <div className="matching-results">
          <div className="match-item">
            <h4>技能匹配度</h4>
            <div className="progress-bar">
              <div className="progress-fill" style={{width: `${planData.skill_match_score || 0}%`}}></div>
            </div>
            <span>{planData.skill_match_score || 0}%</span>
          </div>
          
          <div className="match-item">
            <h4>经验匹配度</h4>
            <div className="progress-bar">
              <div className="progress-fill" style={{width: `${planData.experience_match_score || 0}%`}}></div>
            </div>
            <span>{planData.experience_match_score || 0}%</span>
          </div>
          
          <div className="gap-analysis">
            <h4>差距分析</h4>
            <ul>
              {planData.gap_analysis?.gaps?.map((gap, index) => (
                <li key={index}>
                  {gap.status === 'missing' ? '❌' : '⚠️'} {gap.skill} ({gap.priority} priority)
                </li>
              )) || []}
              {planData.gap_analysis?.strengths?.map((strength, index) => (
                <li key={index}>
                  ✅ {strength.skill} ({strength.status})
                </li>
              )) || []}
            </ul>
          </div>
        </div>
      </div>
    );
  };

  const renderStep4 = () => {
    if (!planData) return <div className="loading">正在生成个性化学习建议...</div>;
    
    return (
      <div className="planner-step">
        <div className="step-header">
          <div className="step-icon">💡</div>
          <div className="step-title-section">
            <h3>定制化建议</h3>
            <p>基于你的技能差距分析生成的个性化学习路径</p>
          </div>
        </div>
        
        {/* 技能匹配度概览 */}
        <div className="match-overview">
          <h4>🎯 技能匹配概览</h4>
          <div className="match-stats">
            <div className="stat-item">
              <span className="stat-label">技能匹配度</span>
              <span className="stat-value">{planData.skill_match_score || 0}%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">经验匹配度</span>
              <span className="stat-value">{planData.experience_match_score || 0}%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">整体匹配度</span>
              <span className="stat-value">{planData.gap_analysis?.overall_match || 0}%</span>
            </div>
          </div>
        </div>
        
        <div className="recommendations">
          {/* 推荐课程 */}
          <div className="recommendation-card">
            <h4>📚 推荐课程</h4>
            <div className="course-list">
              {planData.recommended_courses?.map((course, index) => (
                <div key={index} className="course-item">
                  <div className="course-header">
                    <h5>{course.name}</h5>
                    <span className={`priority-badge ${course.priority || 'medium'}`}>
                      {course.priority || 'medium'} priority
                    </span>
                  </div>
                  <div className="course-details">
                    <p><strong>平台:</strong> {course.platform}</p>
                    <p><strong>难度:</strong> {course.difficulty}</p>
                    <p><strong>时长:</strong> {course.duration}</p>
                    {course.target_skill && (
                      <p><strong>目标技能:</strong> {course.target_skill}</p>
                    )}
                    <p><strong>描述:</strong> {course.description}</p>
                    {course.url && (
                      <a href={course.url} target="_blank" rel="noopener noreferrer" className="course-link">
                        查看课程 →
                      </a>
                    )}
                  </div>
                </div>
              )) || []}
            </div>
          </div>
          
          {/* 推荐项目 */}
          <div className="recommendation-card">
            <h4>💻 项目练习</h4>
            <div className="project-list">
              {planData.recommended_projects?.map((project, index) => (
                <div key={index} className="project-item">
                  <div className="project-header">
                    <h5>{project.name}</h5>
                    <span className={`difficulty-badge ${project.difficulty || 'medium'}`}>
                      {project.difficulty || 'medium'}
                    </span>
                  </div>
                  <div className="project-details">
                    <p><strong>技术栈:</strong> {project.tech_stack?.join(', ')}</p>
                    <p><strong>时长:</strong> {project.duration}</p>
                    <p><strong>描述:</strong> {project.description}</p>
                    {project.learning_objectives && (
                      <div className="learning-objectives">
                        <strong>学习目标:</strong>
                        <ul>
                          {project.learning_objectives.map((objective, idx) => (
                            <li key={idx}>{objective}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {project.target_skills && (
                      <p><strong>目标技能:</strong> {project.target_skills.join(', ')}</p>
                    )}
                  </div>
                </div>
              )) || []}
            </div>
          </div>
          
          {/* 推荐练习 */}
          <div className="recommendation-card">
            <h4>🎤 模拟面试</h4>
            <div className="practice-list">
              {planData.recommended_practice?.map((practice, index) => (
                <div key={index} className="practice-item">
                  <div className="practice-header">
                    <h5>{practice.type}</h5>
                    <span className="frequency-badge">{practice.frequency}</span>
                  </div>
                  <div className="practice-details">
                    <p><strong>重点:</strong> {practice.focus}</p>
                    <p><strong>描述:</strong> {practice.description}</p>
                    {practice.target_skills && (
                      <p><strong>目标技能:</strong> {practice.target_skills.join(', ')}</p>
                    )}
                  </div>
                </div>
              )) || []}
            </div>
          </div>
        </div>
        
        {/* 学习路径 */}
        {planData.recommended_courses?.[0]?.learning_path && (
          <div className="learning-path">
            <h4>🛤️ 学习路径</h4>
            <div className="path-timeline">
              <div className="timeline-item">
                <h5>短期目标 (1-4周)</h5>
                <ul>
                  {planData.recommended_courses[0].learning_path?.short_term?.map((goal, index) => (
                    <li key={index}>{goal}</li>
                  )) || []}
                </ul>
              </div>
              <div className="timeline-item">
                <h5>中期目标 (5-8周)</h5>
                <ul>
                  {planData.recommended_courses[0].learning_path?.medium_term?.map((goal, index) => (
                    <li key={index}>{goal}</li>
                  )) || []}
                </ul>
              </div>
              <div className="timeline-item">
                <h5>长期目标 (9-12周)</h5>
                <ul>
                  {planData.recommended_courses[0].learning_path?.long_term?.map((goal, index) => (
                    <li key={index}>{goal}</li>
                  )) || []}
                </ul>
              </div>
            </div>
          </div>
        )}
        
        {/* 时间线 */}
        {planData.recommended_courses?.[0]?.timeline && (
          <div className="timeline-section">
            <h4>⏰ 预计时间线</h4>
            <div className="timeline-info">
              <p><strong>预计完成时间:</strong> {planData.recommended_courses[0].timeline?.estimated_weeks || 12} 周</p>
              {planData.recommended_courses[0].timeline?.milestones && (
                <div className="milestones">
                  <strong>关键里程碑:</strong>
                  <ul>
                    {planData.recommended_courses[0].timeline.milestones.map((milestone, index) => (
                      <li key={index}>{milestone}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderStep5 = () => {
    if (!planData) return <div className="loading">正在加载进度数据...</div>;
    
    const progress = planData.progress || {};
    
    return (
      <div className="planner-step">
        <div className="step-header">
          <div className="step-icon">📊</div>
          <div className="step-title-section">
            <h3>进度跟踪 & 打卡激励</h3>
            <p>实时跟踪学习进度，获得成就徽章激励</p>
          </div>
        </div>
        
        <div className="progress-tracker">
          <div className="progress-card">
            <h4>课程进度</h4>
            <div className="progress-circle">
              <span>{Math.round(progress.courses?.percentage || 0)}%</span>
            </div>
            <p>已完成 {progress.courses?.completed || 0}/{progress.courses?.total || 0} 门课程</p>
          </div>
          
          <div className="progress-card">
            <h4>项目进度</h4>
            <div className="progress-circle">
              <span>{Math.round(progress.projects?.percentage || 0)}%</span>
            </div>
            <p>已完成 {progress.projects?.completed || 0}/{progress.projects?.total || 0} 个项目</p>
          </div>
          
          <div className="progress-card">
            <h4>面试练习</h4>
            <div className="progress-circle">
              <span>{Math.round(progress.interviews?.percentage || 0)}%</span>
            </div>
            <p>已完成 {progress.interviews?.completed || 0}/{progress.interviews?.target || 5} 次模拟面试</p>
          </div>
        </div>
        
        <div className="achievements">
          <h4>🏆 成就徽章</h4>
          <div className="badges">
            {planData.badges_earned?.map((badge, index) => (
              <div key={index} className="badge earned">{badge}</div>
            )) || []}
            <div className="badge">🎤 面试专家</div>
          </div>
        </div>
      </div>
    );
  };

  const renderStep = () => {
    switch(currentStep) {
      case 1: return renderStep1();
      case 2: return renderStep2();
      case 3: return renderStep3();
      case 4: return renderStep4();
      case 5: return renderStep5();
      default: return renderStep1();
    }
  };

  if (error) {
    return (
      <div className="interview-planner">
        <div className="planner-container">
          <div className="error-message">
            <h3>❌ 错误</h3>
            <p>{error}</p>
            <button onClick={() => setError(null)}>重试</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="interview-planner">
      {/* 背景装饰 */}
      <div className="radial-light-circle top-right" />
      <div className="radial-light-circle bottom-left" />
      
      <div className="planner-header">
        <div className="header-icon">📋</div>
        <div className="header-content">
          <h1>Interview Planner</h1>
          <p>智能面试规划，助你系统提升面试能力</p>
        </div>
      </div>

      <div className="planner-container">
        <div className="step-indicator">
          {[1, 2, 3, 4, 5].map(step => (
            <div 
              key={step} 
              className={`step-dot ${currentStep >= step ? 'active' : ''}`}
              onClick={() => setCurrentStep(step)}
            >
              {step}
            </div>
          ))}
        </div>

        {renderStep()}

        <div className="planner-actions">
          {currentStep > 1 && (
            <button className="btn-secondary" onClick={prevStep} disabled={loading}>
              <span className="btn-icon">←</span> 上一步
            </button>
          )}
          
          {currentStep < 5 ? (
            <button className="btn-primary" onClick={nextStep} disabled={loading}>
              <span className="btn-icon">{loading ? '⏳' : '→'}</span>
              {loading ? '处理中...' : '下一步'}
            </button>
          ) : (
            <button className="btn-primary" onClick={onBackToInterview}>
              <span className="btn-icon">🎤</span> 开始面试
            </button>
          )}
          
          <button className="btn-secondary" onClick={onBackToInterview}>
            <span className="btn-icon">🏠</span> 返回面试助手
          </button>
        </div>
      </div>
    </div>
  );
};

export default InterviewPlanner; 