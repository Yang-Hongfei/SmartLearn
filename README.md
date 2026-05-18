# SmartLearn 智能刷题平台

基于 **知识图谱 + RAG** 的个性化学习平台，支持 PDF 题库导入、多模式刷题、AI 智能判题与诊断分析。

## 项目概述

SmartLearn 是一个全栈智能刷题系统，核心流程为：**上传 PDF 教材 → LLM 自动提取问答对 → 三种模式刷题练习 → AI 判题诊断 → 生成个性化学习路径**。

已成功导入 3 本"面渣逆袭"系列 PDF（分布式篇、Java 基础篇、Spring 篇），共计 152 道题目。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **用户前端** | Vue 3 + Element Plus + Vite | 刷题练习、PDF 导入 |
| **业务后端** | Spring Boot 2.7 + MyBatis | 题库管理、答题记录、判题编排 |
| **AI 服务层** | FastAPI (Python 3.12) | LLM 判题、PDF 解析、RAG、知识图谱 |
| **LLM** | DeepSeek-V4-Flash (deepseek-chat) | 判题诊断、PDF 题目提取、学习建议 |
| **Embedding** | text-embedding-v4（阿里云百炼） | 文本向量化，1024 维 |
| **向量数据库** | Chroma（嵌入式模式） | 本地文件持久化，余弦相似度检索 |
| **图数据库** | Neo4j Community | 知识图谱存储、图遍历、最短路径查询 |
| **关系型数据库** | MySQL 8 | 用户、题库、练习记录、导入历史 |
| **PDF 提取** | Apache PDFBox 2.0 | Java 端流式文本提取 |

## 项目结构

```
SmartLearn智能刷题平台/
├── frontend/                              # Vue 3 用户前端
│   ├── src/
│   │   ├── main.js                        # Vue 入口，注册 Element Plus + Router
│   │   ├── App.vue
│   │   ├── router/index.js                # /practice 刷题页, /import PDF导入页
│   │   ├── api/
│   │   │   ├── client.js                  # Axios 实例 (baseURL → localhost:8080/api)
│   │   │   ├── questionApi.js             # 题库接口
│   │   │   ├── practiceApi.js             # 练习接口
│   │   │   └── pdfApi.js                  # PDF导入接口
│   │   ├── views/
│   │   │   ├── PracticePage.vue           # 刷题练习页（容器组件）
│   │   │   └── PdfImportPage.vue          # PDF导入页
│   │   ├── components/
│   │   │   ├── layout/AppLayout.vue       # 全局布局 (el-container + el-menu)
│   │   │   ├── practice/
│   │   │   │   ├── ModeSelector.vue       # 随机/顺序/错题 模式切换
│   │   │   │   ├── QuestionCard.vue       # 题目卡片（自动选择题型组件）
│   │   │   │   ├── ChoiceOptionList.vue   # 单选/判断题选项 (el-radio-group)
│   │   │   │   ├── FillBlankInput.vue     # 填空/问答题输入 (el-input textarea)
│   │   │   │   ├── ActionBar.vue          # 操作按钮组（提交/跳过/已学会/AI解析）
│   │   │   │   ├── JudgeModeDialog.vue    # 判题模式选择弹窗
│   │   │   │   ├── SelfJudgePanel.vue     # 自主判题面板（显示答案+用户标对错）
│   │   │   │   ├── AiAnalysisPanel.vue    # AI 分析结果弹窗
│   │   │   │   ├── ErrorAnalysisDisplay.vue   # 错题解析展示
│   │   │   │   ├── WeakPointsList.vue     # 薄弱知识点标签 (el-tag)
│   │   │   │   ├── LearningPathTimeline.vue    # 学习路径时间线 (el-timeline)
│   │   │   │   ├── ProgressSidebar.vue    # 右侧统计面板（总数/已学会/未作答/答错）
│   │   │   │   └── NavigationControls.vue # 上一题/下一题 导航
│   │   │   └── pdf/
│   │   │       ├── UploadDragger.vue      # PDF 拖拽上传 (el-upload)
│   │   │       ├── ImportHistoryTable.vue # 导入历史表格 (el-table)
│   │   │       └── ImportResultModal.vue  # 导入结果预览弹窗 (el-dialog)
│   │   └── utils/constants.js             # 题型/状态枚举
│   ├── package.json
│   └── vite.config.js
│
├── springboot-backend/                    # SpringBoot 业务后端
│   ├── pom.xml                            # Java 8, Spring Boot 2.7.18, MyBatis, PDFBox
│   ├── src/main/resources/
│   │   ├── application.yml                # MySQL 配置, AI 地址, 文件上传
│   │   └── db/schema.sql                  # 4 张表 DDL + 默认用户
│   └── src/main/java/com/smartlearn/
│       ├── SmartLearnApplication.java
│       ├── client/AiServiceClient.java    # FastAPI 调用客户端（判题+PDF解析）
│       ├── config/
│       │   ├── AiClientConfig.java        # RestTemplate 600s 超时配置
│       │   └── CorsConfig.java            # 跨域配置
│       ├── controller/
│       │   ├── QuestionController.java    # 题库 CRUD + 随机/顺序/错题查询
│       │   ├── PracticeController.java    # 提交答案 + 自主判题 + AI分析
│       │   └── PdfImportController.java   # PDF 上传 + 导入历史
│       ├── service/
│       │   ├── QuestionService.java       # 题库业务逻辑
│       │   ├── PracticeService.java       # 三种判题模式（auto/self/ai）
│       │   └── PdfImportService.java      # PDF 文本提取 + 分块 + LLM 解析编排
│       ├── mapper/                        # MyBatis Mapper 接口
│       ├── model/
│       │   ├── entity/                    # Question, PracticeRecord, PdfImport, User
│       │   ├── dto/                       # ApiResponse, PageResult, SubmitDTO 等
│       │   └── enums/                     # QuestionType, PracticeStatus
│       └── exception/                     # 全局异常处理
│
├── fastapi-ai/                            # FastAPI AI 服务层
│   ├── app/
│   │   ├── main.py                        # 入口：5 个路由模块 + CORS
│   │   ├── api/
│   │   │   ├── analysis.py                # POST /api/analysis/submit-answer 判题诊断
│   │   │   ├── pdf_parse.py               # POST /api/pdf/parse-qa PDF 题目提取
│   │   │   ├── rag.py                     # POST /api/rag/query 混合检索问答
│   │   │   ├── knowledge.py               # 知识图谱 CRUD + 路径查询
│   │   │   └── learning_path.py           # 学习路径规划
│   │   ├── services/
│   │   │   ├── llm_service.py             # DeepSeek OpenAI 兼容接口调用
│   │   │   ├── embedding_service.py       # 百炼 Embedding 向量化
│   │   │   ├── vector_service.py          # Chroma 向量检索
│   │   │   ├── rag_service.py             # 混合检索 RAG 编排
│   │   │   ├── rerank_service.py          # Cohere Rerank 重排序
│   │   │   ├── analysis_service.py        # 答题诊断 + 薄弱点分析
│   │   │   ├── pdf_parse_service.py       # LLM 提取 Q&A 对
│   │   │   ├── kg_service.py              # Neo4j 图数据库操作
│   │   │   └── path_service.py            # 学习路径生成
│   │   ├── core/
│   │   │   ├── config.py                  # 配置管理（DeepSeek + 百炼 + Neo4j）
│   │   │   └── utils.py                   # JSON 解析、关键词提取
│   │   └── models/schemas.py              # Pydantic 请求/响应模型
│   ├── scripts/
│   │   ├── build_kg.py                    # 知识图谱构建
│   │   └── ingest_docs.py                 # 文档向量化入库
│   ├── requirements.txt
│   └── .env
│
├── start-all.bat                          # Windows 一键启动
├── start-all.sh                           # Linux/Mac 一键启动
└── smartlearn.sql                         # 完整数据库导出（含 152 道题目）
```

## 架构与数据流

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│   Vue 3      │────→│   SpringBoot     │────→│   FastAPI    │
│  :5173       │     │   :8080          │     │   :8000      │
│  用户前端     │     │   业务后端        │     │   AI 服务层  │
└──────────────┘     └────────┬─────────┘     └──────┬───────┘
                              │                      │
                              │ MySQL :3306          │ DeepSeek API
                              │ smartlearn           │ 百炼 Embedding
                              └──────────────────────┘
```

### 判题模式

| 模式 | 题型 | 流程 |
|------|------|------|
| **自动判题** | 选择题、判断题 | 前端提交 → SpringBoot 本地比对答案 → 直接返回对/错 |
| **自主判题** | 问答题 | 前端提交 → SpringBoot 保存答案 → 展示标准答案 → 用户手动标对/错 |
| **AI 判题** | 问答题 | 前端提交 → SpringBoot → FastAPI → DeepSeek LLM 评判 → 返回对错 + 解析 + 薄弱点 + 学习路径 |

### AI 判题深度流程

AI 判题是 SmartLearn 的核心诊断引擎，FastAPI 内部采用 **"规则判题 → LLM 诊断 → Neo4j 补全 → 路径规划"** 四阶段流水线：

```
SpringBoot POST /api/analysis/submit-answer
    │  携带：userId, question(题目+答案), userAnswer, knowledgePointIds
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ FastAPI analysis_service.analyze_answer()                   │
│                                                             │
│  ① 规则判题（Python 本地，不消耗 AI token）                   │
│     _judge(type, userAnswer, correctAnswer)                 │
│     - 选择题/判断题：精确匹配（忽略大小写）                    │
│     - 问答题：精确匹配或包含匹配（容忍格式差异）               │
│     → 产出：is_correct: bool                                │
│                                                             │
│  ② LLM 深度分析（DeepSeek Chat）                             │
│     将题目信息 + 判题结果构造成 prompt，调用 LLM               │
│     → 产出 JSON：                                           │
│       {                                                     │
│         "error_analysis": {                                 │
│           "explanation": "解题思路与核心概念",                │
│           "error_type": "概念混淆/知识漏洞/粗心错误/方法错误", │
│           "error_detail": "针对学生错误的具体分析"            │
│         },                                                  │
│         "weak_point_analysis": [                            │
│           { "knowledge_point_id": "kp_xxx",                 │
│             "knowledge_point_name": "...",                  │
│             "current_mastery": 0.0-1.0,    ← LLM 估算掌握度  │
│             "reason": "判断依据" }                           │
│         ]                                                   │
│       }                                                     │
│                                                             │
│  ③ Neo4j 补全薄弱点（_enrich_weak_points）                   │
│     对题目关联的每个 knowledge_point_id：                     │
│       → MATCH (k:KnowledgePoint {id}) RETURN k              │
│     策略：LLM 分析过的知识点 → 保留 LLM 的判断，              │
│           用 Neo4j 的权威名称替换 LLM 的猜测名称              │
│           LLM 没分析的知识点 → 用 Neo4j 兜底补齐，            │
│           默认掌握度 0.3（答错）或 0.7（答对）                │
│     → 产出：完整的薄弱点列表（确保绑定题目的知识点全覆盖）     │
│                                                             │
│  ④ 学习路径生成（path_service.generate_learning_path）       │
│     薄弱点按掌握度升序 → 从最弱的开始学                       │
│     对每个薄弱点：                                           │
│       → Neo4j: MATCH (k)-[PREREQUISITE*1..]->(prereq)       │
│               追溯前置依赖知识                                 │
│       → 去重合并，确保前置知识点排在前面（拓扑序）             │
│       → LLM: 为每个路径节点生成一句话学习建议                  │
│     → 产出：ordered learning_path [{order, knowledge_point,  │
│              reason}]                                        │
│                                                             │
│  最终组装 → AnswerAnalysisResponse 返回 SpringBoot           │
│    {                                                        │
│      is_correct,           ← ① 规则判题                      │
│      error_analysis,       ← ② LLM 错题解析                  │
│      weak_point_analysis,  ← ③ LLM掌握度 + Neo4j名称的融合   │
│      learning_path         ← ④ Neo4j前置追溯 + LLM建议       │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
```

**各步骤职责分工：**

| 步骤 | 数据来源 | 做什么 | 为什么不让 LLM 全包 |
|------|----------|--------|---------------------|
| ① 判题 | Python 规则 | 判断对/错 | 选择题的判题是确定性的，规则匹配比 LLM 更快更可靠 |
| ② 诊断 | DeepSeek LLM | 错题解析、掌握度估算 | LLM 擅长语义理解，能分析"为什么错"而不仅是"错没错" |
| ③ 补全 | Neo4j 图数据库 | 知识点权威名称、全覆盖 | LLM 可能遗漏或编造知识点名称，Neo4j 保证数据一致性 |
| ④ 路径 | Neo4j 图遍历 + LLM | 前置依赖追溯 + 学习建议 | 图数据库天然适合做关系追溯，LLM 负责生成可读的学习建议 |

### PDF 导入流程

```
用户上传 PDF
  → SpringBoot: PDFBox 按页提取原始文本
  → SpringBoot: 按 5000 字分块，优先在页面边界切分
  → SpringBoot 逐块 → FastAPI POST /api/pdf/parse-qa
  → FastAPI: DeepSeek LLM 从文本中提取 Q&A 对
  → SpringBoot: 合并去重，批量写入 questions 表
  → 前端轮询进度：chunks_completed / total_chunks
```

## API 接口

### SpringBoot 业务接口

**题库 (QuestionController)**
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/questions` | 分页列表 |
| GET | `/api/questions/{id}` | 题目详情 |
| GET | `/api/questions/random` | 随机一题（排除已学会） |
| GET | `/api/questions/next` | 下一题（支持 topic 筛选） |
| GET | `/api/questions/prev` | 上一题（支持 topic 筛选） |
| GET | `/api/questions/count` | 题目总数 |
| GET | `/api/questions/topics` | 所有分类列表 |
| GET | `/api/questions/incorrect` | 错题列表 |
| DELETE | `/api/questions/{id}` | 删除题目 |

**练习 (PracticeController)**
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/practice/submit` | 提交答案（judgeMode: auto/self/ai） |
| PUT | `/api/practice/{id}/self-judge` | 自主判题：手动标对错 |
| PUT | `/api/practice/{id}/status` | 更新状态（learned/unanswered） |
| POST | `/api/practice/{id}/ai-analysis` | 对已有记录触发 AI 分析 |
| GET | `/api/practice/records` | 练习记录列表 |
| GET | `/api/practice/stats` | 用户统计（总数/已学会/未作答/答错） |

**PDF 导入 (PdfImportController)**
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/pdf/upload` | 上传 PDF |
| GET | `/api/pdf/imports` | 导入历史列表 |
| GET | `/api/pdf/imports/{id}` | 导入详情 |
| DELETE | `/api/pdf/imports/{id}` | 删除导入及关联题目 |

### FastAPI AI 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/analysis/submit-answer` | 答题诊断（对错 + 解析 + 薄弱点 + 学习路径） |
| POST | `/api/pdf/parse-qa` | PDF 分块文本 → 提取 Q&A 对 |
| POST | `/api/rag/query` | RAG 混合检索智能问答 |
| POST | `/api/knowledge/search` | 搜索知识点 |
| GET | `/api/knowledge/point/{id}` | 查询单个知识点 |
| POST | `/api/knowledge/path` | 两知识点间最短路径 |
| POST | `/api/learning-path/generate` | 生成个性化学习路径 |
| GET | `/api/health` | 健康检查 |

### 统一响应格式

```json
{ "code": 200, "message": "success", "data": {...} }
```

## 快速开始

### 前置条件

- Java 8+
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Neo4j 4.x+（可选，知识图谱功能需要）
- Maven 3.6+

### 1. 数据库初始化

```bash
mysql -u root -p < springboot-backend/src/main/resources/db/schema.sql
# 密码: 666666
```

如需导入已有题库数据：
```bash
mysql -u root -p smartlearn < smartlearn.sql
```

### 2. 配置 .env 环境变量

项目涉及三套配置，分别对应 FastAPI、SpringBoot 和前端。其中 **FastAPI 的 `.env` 文件是唯一需要手动创建的配置文件**，其余已内置默认值。

#### 2.1 FastAPI 环境变量（必配）

`fastapi-ai/.env` 是核心配置文件，控制 LLM、Embedding、向量数据库和图数据库的连接。项目提供了 `.env.example` 模板文件：

```bash
cd fastapi-ai
cp .env.example .env   # 从模板复制一份
```

编辑 `fastapi-ai/.env`，填入以下配置：

```env
# ==================== DeepSeek API（LLM — 必填）====================
# 获取地址：https://platform.deepseek.com/api_keys
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here

# ==================== Embedding（阿里云百炼 — 必填）====================
# 获取地址：https://dashscope.console.aliyun.com/apiKey
# 说明：DeepSeek 暂不提供 Embedding API，向量化仍使用百炼
EMBEDDING_API_KEY=sk-your-embedding-api-key-here

# ==================== LLM 与 Embedding 模型 ====================
LLM_MODEL=deepseek-chat           # DeepSeek-V4-Flash
EMBEDDING_MODEL=text-embedding-v4 # 百炼 1024 维
EMBEDDING_DIMENSIONS=1024

# ==================== Chroma 向量数据库 ====================
CHROMA_PATH=./chroma_data         # 本地持久化路径，默认即可

# ==================== Neo4j 图数据库（可选）====================
# 如不使用知识图谱功能，可保持默认值
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=Neo4j123456

# ==================== Cohere Rerank（可选）====================
# 不填则自动跳过重排序步骤
COHERE_API_KEY=your-cohere-key-here

# ==================== RAG 检索参数（可选）====================
RAG_TOP_K=5
RAG_VECTOR_WEIGHT=0.7
RAG_KEYWORD_WEIGHT=0.3
```

**必填项：** `DEEPSEEK_API_KEY` 和 `EMBEDDING_API_KEY`，缺少任何一个 AI 功能将无法工作。

#### 2.2 SpringBoot 配置（已有默认值）

SpringBoot 配置位于 `springboot-backend/src/main/resources/application.yml`，无需额外创建文件：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `spring.datasource.url` | `jdbc:mysql://localhost:3306/smartlearn` | MySQL 连接 |
| `spring.datasource.username` | `root` | 数据库用户名 |
| `spring.datasource.password` | `666666` | 数据库密码 |
| `smartlearn.ai.base-url` | `http://localhost:8000` | FastAPI 地址 |
| `smartlearn.upload.path` | `springboot-backend/uploads/` | PDF 上传目录 |

如数据库密码或 FastAPI 地址不同，直接修改该文件即可。

#### 2.3 前端配置（已有默认值）

前端无需 `.env` 文件。开发环境下 Vite 自动将 `/api` 请求代理到 `http://localhost:8080`（配置在 `frontend/vite.config.js`）。如需修改后端地址，编辑 `vite.config.js` 中的 proxy 配置。

### 3. 安装依赖

```bash
# FastAPI
cd fastapi-ai
pip install -r requirements.txt

# SpringBoot — Maven 自动下载依赖，无需手动操作

# Vue 前端
cd frontend
npm install
```

### 4. 一键启动

**Windows：** 双击 `start-all.bat`
**Linux/Mac：** `bash start-all.sh`

或手动启动各服务：

```bash
# 1. FastAPI（先启动）
cd fastapi-ai
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. SpringBoot
cd springboot-backend
mvn spring-boot:run

# 3. Vue 前端
cd frontend
npm run dev
```

### 5. 访问

| 服务 | 地址 | 用途 |
|------|------|------|
| Vue 前端 | `http://localhost:5173` | 用户界面 |
| SpringBoot | `http://localhost:8080` | 业务 API |
| FastAPI Swagger | `http://localhost:8000/docs` | AI API 文档 |

## 刷题功能

### 三种模式

| 模式 | 说明 |
|------|------|
| **随机刷题** | 从题库随机取题（排除已学会的题） |
| **顺序刷题** | 按题目 ID 顺序练习，支持按分类筛选 |
| **刷错题** | 仅练习 status=incorrect 的题目 |

### 题目状态

| 状态 | 含义 |
|------|------|
| 未作答 | 尚未练习过的题目 |
| 答错 | 回答错误的题目，可反复练习 |
| 已学会 | 用户标记为已掌握的题目，不再出现在随机模式中 |

### 操作按钮

- **提交** — 提交答案。选择题/判断题自动判题；问答题弹出判题模式选择
- **跳过** — 跳过当前题，加载下一题
- **已学会** — 将当前题标记为已掌握
- **AI 解析** — 对已提交的记录补看 AI 诊断分析

## 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| Vue 3 Dev Server | 5173 | 前端开发服务器 |
| SpringBoot | 8080 | 业务后端 |
| FastAPI | 8000 | AI 服务 |
| MySQL | 3306 | 关系型数据库 |
| Neo4j Browser | 7474 | 图数据库管理（可选） |
