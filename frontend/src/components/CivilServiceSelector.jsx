import React, { useState } from 'react';

const CIVIL_SERVICE_TYPES = [
  {
    id: 'national',
    name: '国考',
    description: '国家公务员考试',
    icon: '🏛️',
    subTypes: [
      { id: 'administrative', name: '行政职业能力测验', icon: '📋' },
      { id: 'application', name: '申论', icon: '✍️' },
      { id: 'interview', name: '面试', icon: '🎤' }
    ]
  },
  {
    id: 'provincial',
    name: '省考',
    description: '省级公务员考试',
    icon: '🏢',
    subTypes: [
      { id: 'administrative', name: '行政职业能力测验', icon: '📋' },
      { id: 'application', name: '申论', icon: '✍️' },
      { id: 'interview', name: '面试', icon: '🎤' }
    ]
  },
  {
    id: 'municipal',
    name: '市考',
    description: '市级公务员考试',
    icon: '🏘️',
    subTypes: [
      { id: 'administrative', name: '行政职业能力测验', icon: '📋' },
      { id: 'application', name: '申论', icon: '✍️' },
      { id: 'interview', name: '面试', icon: '🎤' }
    ]
  }
];

const PROVINCES = [
  { id: 'beijing', name: '北京市', code: '11' },
  { id: 'tianjin', name: '天津市', code: '12' },
  { id: 'hebei', name: '河北省', code: '13' },
  { id: 'shanxi', name: '山西省', code: '14' },
  { id: 'neimenggu', name: '内蒙古自治区', code: '15' },
  { id: 'liaoning', name: '辽宁省', code: '21' },
  { id: 'jilin', name: '吉林省', code: '22' },
  { id: 'heilongjiang', name: '黑龙江省', code: '23' },
  { id: 'shanghai', name: '上海市', code: '31' },
  { id: 'jiangsu', name: '江苏省', code: '32' },
  { id: 'zhejiang', name: '浙江省', code: '33' },
  { id: 'anhui', name: '安徽省', code: '34' },
  { id: 'fujian', name: '福建省', code: '35' },
  { id: 'jiangxi', name: '江西省', code: '36' },
  { id: 'shandong', name: '山东省', code: '37' },
  { id: 'henan', name: '河南省', code: '41' },
  { id: 'hubei', name: '湖北省', code: '42' },
  { id: 'hunan', name: '湖南省', code: '43' },
  { id: 'guangdong', name: '广东省', code: '44' },
  { id: 'guangxi', name: '广西壮族自治区', code: '45' },
  { id: 'hainan', name: '海南省', code: '46' },
  { id: 'chongqing', name: '重庆市', code: '50' },
  { id: 'sichuan', name: '四川省', code: '51' },
  { id: 'guizhou', name: '贵州省', code: '52' },
  { id: 'yunnan', name: '云南省', code: '53' },
  { id: 'xizang', name: '西藏自治区', code: '54' },
  { id: 'shaanxi', name: '陕西省', code: '61' },
  { id: 'gansu', name: '甘肃省', code: '62' },
  { id: 'qinghai', name: '青海省', code: '63' },
  { id: 'ningxia', name: '宁夏回族自治区', code: '64' },
  { id: 'xinjiang', name: '新疆维吾尔自治区', code: '65' }
];

const CivilServiceSelector = ({ onSelect, selectedConfig = null }) => {
  const [selectedType, setSelectedType] = useState(selectedConfig?.type || '');
  const [selectedSubType, setSelectedSubType] = useState(selectedConfig?.subType || '');
  const [selectedProvince, setSelectedProvince] = useState(selectedConfig?.province || '');
  const [examYear, setExamYear] = useState(selectedConfig?.examYear || new Date().getFullYear());
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleTypeSelect = (typeId) => {
    setSelectedType(typeId);
    setSelectedSubType(''); // 重置子类型
  };

  const handleSubTypeSelect = (subTypeId) => {
    setSelectedSubType(subTypeId);
  };

  const handleProvinceSelect = (provinceId) => {
    setSelectedProvince(provinceId);
  };

  const handleStartPractice = () => {
    if (!selectedType || !selectedSubType) {
      alert('请选择考试类型和科目');
      return;
    }

    const config = {
      type: selectedType,
      subType: selectedSubType,
      province: selectedProvince,
      examYear: examYear,
      examName: `${CIVIL_SERVICE_TYPES.find(t => t.id === selectedType)?.name} - ${
        CIVIL_SERVICE_TYPES.find(t => t.id === selectedType)?.subTypes.find(st => st.id === selectedSubType)?.name
      }`
    };

    onSelect(config);
  };

  const selectedTypeData = CIVIL_SERVICE_TYPES.find(t => t.id === selectedType);
  const selectedProvinceData = PROVINCES.find(p => p.id === selectedProvince);

  return (
    <div className="civil-service-selector">
      <div className="selector-header">
        <h2>
          <span className="icon-title enhanced-icon">🏛️</span>
          考公面试选择器
        </h2>
        <p className="selector-description">
          选择考试类型和地区，开始考公面试练习
        </p>
      </div>

      {/* 考试类型选择 */}
      <div className="section-card">
        <h3>📋 选择考试类型</h3>
        <div className="type-grid">
          {CIVIL_SERVICE_TYPES.map((type) => (
            <div
              key={type.id}
              className={`type-card ${selectedType === type.id ? 'selected' : ''}`}
              onClick={() => handleTypeSelect(type.id)}
            >
              <div className="type-icon">{type.icon}</div>
              <div className="type-info">
                <h4>{type.name}</h4>
                <p>{type.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 考试科目选择 */}
      {selectedType && (
        <div className="section-card">
          <h3>📚 选择考试科目</h3>
          <div className="subtype-grid">
            {selectedTypeData?.subTypes.map((subType) => (
              <div
                key={subType.id}
                className={`subtype-card ${selectedSubType === subType.id ? 'selected' : ''}`}
                onClick={() => handleSubTypeSelect(subType.id)}
              >
                <div className="subtype-icon">{subType.icon}</div>
                <div className="subtype-info">
                  <h4>{subType.name}</h4>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 地区选择 */}
      {selectedType && selectedSubType && (
        <div className="section-card">
          <h3>📍 选择考试地区</h3>
          <div className="province-selector">
            <select
              value={selectedProvince}
              onChange={(e) => handleProvinceSelect(e.target.value)}
              className="province-select"
            >
              <option value="">请选择地区</option>
              {PROVINCES.map((province) => (
                <option key={province.id} value={province.id}>
                  {province.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* 高级设置 */}
      {selectedType && selectedSubType && (
        <div className="section-card">
          <div className="advanced-toggle">
            <button
              className="btn btn-outline"
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              {showAdvanced ? '收起' : '展开'} 高级设置
            </button>
          </div>
          
          {showAdvanced && (
            <div className="advanced-settings">
              <div className="setting-item">
                <label>考试年份：</label>
                <select
                  value={examYear}
                  onChange={(e) => setExamYear(parseInt(e.target.value))}
                  className="year-select"
                >
                  {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map(year => (
                    <option key={year} value={year}>{year}年</option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 开始练习按钮 */}
      {selectedType && selectedSubType && (
        <div className="section-card">
          <div className="config-summary">
            <h3>📝 练习配置</h3>
            <div className="summary-items">
              <div className="summary-item">
                <span className="label">考试类型：</span>
                <span className="value">{selectedTypeData?.name}</span>
              </div>
              <div className="summary-item">
                <span className="label">考试科目：</span>
                <span className="value">
                  {selectedTypeData?.subTypes.find(st => st.id === selectedSubType)?.name}
                </span>
              </div>
              {selectedProvince && (
                <div className="summary-item">
                  <span className="label">考试地区：</span>
                  <span className="value">{selectedProvinceData?.name}</span>
                </div>
              )}
              <div className="summary-item">
                <span className="label">考试年份：</span>
                <span className="value">{examYear}年</span>
              </div>
            </div>
          </div>
          
          <div className="action-buttons">
            <button
              className="btn btn-primary btn-fancy"
              onClick={handleStartPractice}
              disabled={!selectedType || !selectedSubType}
            >
              <span className="btn-icon">🚀</span>
              开始考公练习
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CivilServiceSelector; 