# Interview Helper 系统完整流程图 (可导出版本)

## 系统概述

Interview Helper是一个AI驱动的面试陪练平台，支持语音和文本交互，提供个性化的面试反馈和改进建议。系统在现有功能基础上新增了针对考公面试的专门功能模块。

## 1. 系统整体架构图

```mermaid
graph LR
    %% 用户层
    subgraph "用户层 (User Layer)"
        A[用户] 
        B[Web浏览器]
        C[移动端]
        A --> B
        A --> C
    end
    
    %% 前端层
    subgraph "前端层 (Frontend Layer)"
        D[App.jsx 主应用]
        E[JobSelector.jsx 职位选择器]
        F[JobDescUpload.jsx 职位描述上传]
        G[ChatWindow.jsx 聊天窗口]
        H[InterviewSession.jsx 面试会话管理]
        I[FeedbackPanel.jsx 反馈面板]
        J[VoiceRecorder.jsx 语音录制]
        K[CivilServiceSelector.jsx 考公面试选择器]
        L[CivilServiceInterview.jsx 考公面试界面]
        M[移动端适配组件]
        
        D --> E
        D --> F
        D --> G
        D --> H
        D --> I
        D --> J
        D --> K
        D --> L
        D --> M
    end
    
    %% API网关层
    subgraph "API网关层 (API Gateway)"
        N[app.py FastAPI服务]
        O[认证授权]
        P[请求路由]
        Q[响应处理]
        R[CORS中间件]
        
        N --> O
        N --> P
        N --> Q
        N --> R
    end
    
    %% 业务逻辑层
    subgraph "业务逻辑层 (Business Logic)"
        S[RAG Pipeline 对话生成]
        T[AI对话生成]
        U[反馈分析]
        V[AI打分生成]
        W[Civil Service Agent 考公面试智能体]
        X[考公面试专用]
        Y[结构化评价]
        Z[标准答案对比]
        
        S --> T
        S --> U
        S --> V
        W --> X
        W --> Y
        W --> Z
    end
    
    %% 数据层
    subgraph "数据层 (Data Layer)"
        AA[SQLite数据库]
        BB[用户数据]
        CC[职位数据]
        DD[面试会话]
        EE[问题反馈]
        FF[考公面试数据]
        GG[知识库]
        HH[考公面试题库]
        II[标准答案库]
        JJ[职位知识库]
        
        AA --> BB
        AA --> CC
        AA --> DD
        AA --> EE
        AA --> FF
        GG --> HH
        GG --> II
        GG --> JJ
    end
    
    %% 外部服务
    subgraph "外部服务 (External Services)"
        KK[OpenAI API]
        LL[GPT-4o-mini LLM]
        MM[Whisper ASR 语音识别]
        NN[TTS 语音合成]
        
        KK --> LL
        KK --> MM
        KK --> NN
    end
    
    %% 连接关系
    A --> D
    D --> N
    N --> S
    N --> W
    S --> AA
    W --> GG
    S --> KK
    W --> KK
    
    %% 样式
    classDef userLayer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef frontendLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef apiLayer fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef businessLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef dataLayer fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef externalLayer fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    
    class A,B,C userLayer
    class D,E,F,G,H,I,J,K,L,M frontendLayer
    class N,O,P,Q,R apiLayer
    class S,T,U,V,W,X,Y,Z businessLayer
    class AA,BB,CC,DD,EE,FF,GG,HH,II,JJ dataLayer
    class KK,LL,MM,NN externalLayer
```

## 2. 用户交互完整流程图

```mermaid
sequenceDiagram
    participant User as 用户
    participant Frontend as 前端界面
    participant Backend as 后端服务
    participant AI as AI服务
    participant DB as 数据库
    participant KB as 知识库
    
    Note over User,KB: 系统启动流程
    User->>Frontend: 1. 访问Interview Helper
    Frontend->>User: 显示主界面
    
    User->>Frontend: 2. 选择面试模式
    Note over User,Frontend: 用户选择: 普通面试 / 考公面试
    
    alt 普通面试模式
        User->>Frontend: 3a. 选择职位类型
        Frontend->>Backend: GET /api/jobs 获取职位列表
        Backend->>DB: 查询职位数据
        DB->>Backend: 返回职位列表
        Backend->>Frontend: 返回职位数据
        Frontend->>User: 显示职位选择器
        
        User->>Frontend: 4a. 上传职位描述
        Frontend->>Backend: POST /api/upload-job-desc 上传JD
        Backend->>AI: 分析JD内容
        AI->>Backend: 返回JD分析结果
        Backend->>Frontend: 返回处理结果
        Frontend->>User: 显示JD确认界面
        
        User->>Frontend: 5a. 获取面试建议
        Frontend->>Backend: POST /api/jd_advice 获取建议
        Backend->>AI: 生成面试建议
        AI->>Backend: 返回建议内容
        Backend->>Frontend: 返回建议
        Frontend->>User: 显示面试建议
        
    else 考公面试模式
        User->>Frontend: 3b. 选择考公岗位类型
        Frontend->>Backend: GET /api/civil-service/positions
        Backend->>DB: 查询考公岗位数据
        DB->>Backend: 返回岗位数据
        Backend->>Frontend: 返回岗位列表
        Frontend->>User: 显示考公岗位选择器
        
        User->>Frontend: 4b. 选择面试类型
        Frontend->>Backend: GET /api/civil-service/interview-formats
        Backend->>KB: 查询考公面试知识库
        KB->>Backend: 返回面试类型数据
        Backend->>Frontend: 返回配置数据
        Frontend->>User: 显示面试类型选择器
    end
    
    Note over User,KB: 面试开始流程
    User->>Frontend: 6. 开始面试
    Frontend->>Backend: POST /api/sessions/start 或 /api/civil-service/start
    Backend->>DB: 创建面试会话
    DB->>Backend: 确认保存
    Backend->>AI: 生成第一个问题
    AI->>Backend: 返回AI问题
    Backend->>Frontend: 返回会话ID和第一个问题
    Frontend->>User: 进入面试界面
    
    Note over User,KB: 面试问答循环
    loop 面试问答循环
        alt 文本模式
            User->>Frontend: 输入回答
            Frontend->>Backend: 发送用户回答
        else 语音模式
            User->>Frontend: 录制语音回答
            Frontend->>Backend: 发送音频文件
            Backend->>AI: 语音转文字
            AI->>Backend: 返回转写文本
            
            alt 录音失败处理
                Backend->>Frontend: 录音失败错误
                Frontend->>User: 显示录音失败提示
                User->>Frontend: 选择重试录音
                Frontend->>Backend: 重新发送音频文件
                Backend->>AI: 重新语音转文字
                AI->>Backend: 返回转写文本
            end
        end
        
        Backend->>AI: 生成下一个问题
        AI->>Backend: 返回AI问题
        Backend->>AI: 分析用户回答
        AI->>Backend: 返回反馈和评分
        Backend->>DB: 保存问答记录
        Backend->>Frontend: 返回AI响应
        Frontend->>User: 显示AI问题和反馈
        
        alt 语音模式
            Backend->>AI: 文本转语音
            AI->>Backend: 返回音频流
            Backend->>Frontend: 流式传输音频
            Frontend->>User: 播放AI语音
        end
    end
    
    Note over User,KB: 面试结束流程
    User->>Frontend: 结束面试
    Frontend->>Backend: 结束会话
    Backend->>AI: 生成最终评价
    AI->>Backend: 返回综合评价
    Backend->>DB: 保存最终结果
    Backend->>Frontend: 返回最终反馈
    Frontend->>User: 显示面试总结
```

## 3. 考公面试智能体详细流程

```mermaid
graph TD
    A[用户选择考公面试模式] --> B[选择考公岗位类型]
    B --> C{岗位类型选择}
    
    C -->|公务员| D[公务员面试题库]
    C -->|事业编| E[事业编面试题库]
    C -->|教师| F[教师面试题库]
    C -->|警察| G[警察面试题库]
    C -->|其他| H[通用考公题库]
    
    D --> I[选择面试形式]
    E --> I
    F --> I
    G --> I
    H --> I
    
    I --> J{面试形式选择}
    J -->|结构化面试| K[结构化面试流程]
    J -->|半结构化面试| L[半结构化面试流程]
    J -->|无领导小组讨论| M[无领导小组讨论流程]
    
    K --> N[AI生成结构化问题]
    L --> O[AI生成半结构化问题]
    M --> P[AI生成讨论题目]
    
    N --> Q[用户回答]
    O --> Q
    P --> Q
    
    Q --> R[AI分析回答]
    R --> S{STAR结构分析}
    
    S -->|符合STAR结构| T[给予正面反馈]
    S -->|部分符合| U[指出不足并建议]
    S -->|不符合| V[详细指导改进]
    
    T --> W[生成下一个问题]
    U --> W
    V --> W
    
    W --> X{是否继续面试}
    X -->|是| Q
    X -->|否| Y[生成最终评价]
    
    %% 用户控制行为
    X -->|用户手动跳题| Z[跳过当前问题]
    X -->|用户手动结束| Y
    Z --> W
    
    Y --> AA[结构化评价报告]
    AA --> BB[改进建议]
    BB --> CC[推荐练习方向]
    CC --> DD[面试总结]
    
    %% 样式定义
    classDef startNode fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef processNode fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decisionNode fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef endNode fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef userControlNode fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class A startNode
    class B,I,J processNode
    class C,X decisionNode
    class DD endNode
    class Z userControlNode
```

## 4. 数据流架构图

```mermaid
graph LR
    %% 输入层
    subgraph "输入层 (Input Layer)"
        A[用户语音输入]
        B[用户文本输入]
        C[职位描述文件]
        D[考公面试配置]
        E[面试模式选择]
    end
    
    %% 处理层
    subgraph "处理层 (Processing Layer)"
        F[语音转文字 ASR]
        G[文本预处理]
        H[JD解析分析]
        I[考公知识库查询]
        J[面试类型识别]
    end
    
    %% AI服务层
    subgraph "AI服务层 (AI Service Layer)"
        K[GPT-4o-mini LLM]
        L[Whisper ASR]
        M[TTS语音合成]
        N[考公面试智能体]
        O[RAG Pipeline]
        P[Prompt构建]
    end
    
    %% 输出层
    subgraph "输出层 (Output Layer)"
        Q[AI问题生成]
        R[结构化反馈]
        S[评分计算]
        T[语音输出]
        U[改进建议]
        V[面试建议]
    end
    
    %% 存储层
    subgraph "存储层 (Storage Layer)"
        W[SQLite数据库]
        X[考公面试知识库]
        Y[标准答案库]
        Z[用户会话记录]
        AA[职位知识库]
        BB[系统日志库]
    end
    
    %% 数据流连接
    A --> F
    B --> G
    C --> H
    D --> I
    E --> J
    
    F --> K
    G --> P
    P --> K
    H --> K
    I --> N
    J --> O
    
    K --> Q
    K --> R
    K --> S
    N --> U
    O --> V
    
    Q --> W
    R --> W
    S --> W
    U --> W
    V --> W
    
    I --> X
    N --> Y
    K --> Z
    O --> AA
    F --> BB
    G --> BB
    H --> BB
    I --> BB
    J --> BB
    
    %% 样式定义
    classDef inputLayer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef processingLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef aiLayer fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef outputLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef storageLayer fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class A,B,C,D,E inputLayer
    class F,G,H,I,J processingLayer
    class K,L,M,N,O,P aiLayer
    class Q,R,S,T,U,V outputLayer
    class W,X,Y,Z,AA,BB storageLayer
```

## 5. 系统组件交互图

```mermaid
graph LR
    %% 前端组件
    subgraph "前端组件 (Frontend Components)"
        A[App.jsx 主应用]
        B[JobSelector.jsx 职位选择器]
        C[JobDescUpload.jsx 职位描述上传]
        D[ChatWindow.jsx 聊天窗口]
        E[InterviewSession.jsx 面试会话管理]
        F[FeedbackPanel.jsx 反馈面板]
        G[VoiceRecorder.jsx 语音录制]
        H[CivilServiceSelector.jsx 考公面试选择器]
        I[CivilServiceInterview.jsx 考公面试界面]
        
        A --> B
        A --> C
        A --> D
        A --> E
        A --> F
        A --> G
        A --> H
        A --> I
    end
    
    %% 后端服务
    subgraph "后端服务 (Backend Services)"
        J[app.py 主服务]
        K[RAG Pipeline 对话生成]
        L[Civil Service Agent 考公面试智能体]
        M[Database Models 数据模型]
        N[TTS Service 语音合成服务]
        O[ASR Service 语音识别服务]
        
        J --> K
        J --> L
        J --> M
        J --> N
        J --> O
    end
    
    %% 数据模型
    subgraph "数据模型 (Data Models)"
        P[User 用户]
        Q[InterviewSession 面试会话]
        R[Question 问题]
        S[CivilServicePosition 考公岗位]
        T[CivilServiceSession 考公面试会话]
        U[CivilServiceQARecord 考公问答记录]
        V[Job 职位]
        
        P --> Q
        Q --> R
        S --> T
        T --> U
        V --> Q
    end
    
    %% 外部API
    subgraph "外部API (External APIs)"
        W[OpenAI GPT-4o-mini]
        X[OpenAI Whisper]
        Y[OpenAI TTS]
    end
    
    %% 连接关系
    A --> J
    J --> K
    J --> L
    K --> W
    L --> W
    J --> X
    J --> Y
    K --> P
    L --> S
    
    %% 图例
    subgraph "图例 (Legend)"
        Z1[前端组件]
        Z2[后端服务]
        Z3[数据模型]
        Z4[外部API]
    end
    
    %% 样式定义
    classDef frontendComp fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef backendService fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef dataModel fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef externalAPI fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef legendItem fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px
    
    class A,B,C,D,E,F,G,H,I frontendComp
    class J,K,L,M,N,O backendService
    class P,Q,R,S,T,U,V dataModel
    class W,X,Y externalAPI
    class Z1,Z2,Z3,Z4 legendItem
```

## 6. 面试流程状态图

```mermaid
stateDiagram-v2
    [*] --> 主界面
    主界面 --> 选择面试模式: 用户选择
    选择面试模式 --> 普通面试: 选择普通面试
    选择面试模式 --> 考公面试: 选择考公面试
    
    普通面试 --> 职位选择: 选择职位
    职位选择 --> 职位描述上传: 上传JD
    职位描述上传 --> 面试建议: 获取建议
    面试建议 --> 开始面试: 开始面试
    开始面试 --> 面试进行中: 问答循环
    
    考公面试 --> 考公岗位选择: 选择岗位
    考公岗位选择 --> 面试形式选择: 选择形式
    面试形式选择 --> 考公面试进行中: 开始面试
    考公面试进行中 --> 面试进行中: 问答循环
    
    面试进行中 --> 面试进行中: 继续问答<br/>生成新问题
    面试进行中 --> 面试结束: 结束面试
    面试结束 --> 反馈展示: 显示反馈
    反馈展示 --> 主界面: 返回主页
    
    note right of 主界面
        用户首次访问系统
        显示功能选择界面
    end note
    
    note right of 面试进行中
        用户与AI进行问答交互
        支持语音和文本输入
        实时生成反馈和评分
        自动生成下一个问题
    end note
    
    note right of 反馈展示
        显示面试总结报告
        提供改进建议
        推荐练习方向
    end note
```

## 7. 错误处理流程

```mermaid
graph TD
    A[用户操作] --> B{操作是否成功}
    B -->|是| C[正常流程]
    B -->|否| D[错误处理]
    
    D --> E{错误类型}
    E -->|网络错误| F[重试机制]
    E -->|API错误| G[错误提示]
    E -->|数据错误| H[数据验证]
    E -->|权限错误| I[权限检查]
    
    F --> J{重试次数}
    J -->|小于3次| K[自动重试]
    J -->|3次及以上| L[手动重试提示]
    
    G --> M[显示错误信息]
    H --> N[数据修正]
    I --> O[重新认证]
    
    K --> B
    L --> P[用户确认重试]
    M --> Q[写入错误日志]
    N --> B
    O --> B
    
    P --> B
    Q --> R[错误分析]
    R --> S[系统优化]
    
    %% 错误日志写入路径
    F --> Q
    G --> Q
    H --> Q
    I --> Q
    L --> Q
    M --> Q
    N --> Q
    O --> Q
    
    %% 样式定义
    classDef startNode fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef decisionNode fill:#ff9800,stroke:#f57c00,stroke-width:2px
    classDef processNode fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef endNode fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef logNode fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class A startNode
    class B,E,J decisionNode
    class C,D,F,G,H,I,K,L,M,N,O,P,R,S processNode
    class Q logNode
```

## 导出说明

### 如何导出图片

1. **使用Mermaid Live Editor**:
   - 访问 https://mermaid.live/
   - 复制上述Mermaid代码到编辑器
   - 点击导出按钮，选择PNG、SVG或PDF格式

2. **使用VS Code**:
   - 安装Mermaid Preview插件
   - 在Markdown文件中查看预览
   - 右键选择导出图片

3. **使用在线工具**:
   - Mermaid Chart: https://www.mermaidchart.com/
   - 支持多种导出格式

### 推荐导出格式

- **PNG**: 适合网页展示和文档插入
- **SVG**: 适合网页，可缩放不失真
- **PDF**: 适合打印和正式文档

### 图片尺寸建议

- **系统架构图**: 1200x800px
- **流程图**: 1000x600px
- **状态图**: 800x600px

这些流程图包含了详细的文字描述和清晰的视觉结构，可以直接用于项目文档、演示文稿或技术规范中。 