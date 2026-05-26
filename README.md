# SmartLearn — 基于知识图谱与复合 Agent 范式的自适应学习平台

支持 PDF 题库导入、智能刷题、AI 带学三种学习模式，融合知识图谱、RAG 检索增强生成与 Plan-Execute-Reflect-RePlan Agent 闭环。

## 技术栈

| 层级 | 技术 |
|------|------|
| 用户前端 | Vue 3 + Vite |
| 业务后端 | Spring Boot 2.7 + MyBatis + Java 8 |
| AI 服务层 | FastAPI + LangChain + OpenAI SDK |
| LLM | DeepSeek（deepseek-chat） |
| Embedding | 阿里云百炼 text-embedding-v4（1024 维） |
| 向量数据库 | Chroma（嵌入式） |
| 图数据库 | Neo4j（693 节点 / 2354 关系） |
| 关系数据库 | MySQL 8 |
| PDF 解析 | Apache PDFBox 2.0 |

## 项目结构

```
├── frontend/                     # Vue 3 前端
│   └── src/
│       ├── views/                # HomePage, PracticePage, PdfImportPage, LearnHubPage, LearnSessionPage
│       ├── components/
│       │   ├── practice/         # 刷题组件（QuestionCard, ModeSelector, AiAnalysisPanel 等）
│       │   ├── learn/            # AI 带学组件（ExplainView, QuizView, PathTimeline, ReflectionLog）
│       │   ├── pdf/              # PDF 导入组件
│       │   ├── common/           # 通用组件（SettingsModal）
│       │   └── layout/           # 布局组件
│       ├── api/                  # axios API 模块（client, learnApi, configApi 等）
│       └── router/               # 路由配置
│
├── springboot-backend/           # Spring Boot 业务后端
│   └── src/main/java/com/smartlearn/
│       ├── controller/           # REST 控制器（Question, Practice, PdfImport, Learn, Config）
│       ├── service/              # 业务逻辑
│       ├── client/               # FastAPI 调用客户端（AiServiceClient）
│       ├── mapper/               # MyBatis 注解式 Mapper
│       ├── model/                # entity / dto / enums
│       └── config/               # CORS, ApiKey 过滤器
│
├── fastapi-ai/                   # FastAPI AI 服务
│   └── app/
│       ├── api/                  # analysis, pdf_parse, learning_agent, rag, knowledge, learning_path
│       ├── services/             # llm_service, rag_service, analysis_service, kg_service 等
│       └── core/                 # config, utils
│
└── start-all.bat                 # Windows 一键启动
```

## 快速开始

### 前置条件

- Java 8 / Python 3.10+ / Node.js 18+ / MySQL 8 / Maven

### 1. 数据库

```bash
mysql -u root -p666666 < springboot-backend/src/main/resources/db/schema.sql
```

### 2. 配置 API Key

FastAPI 需要 DeepSeek API Key。启动后可在前端界面右上角齿轮图标处填写，Key 保存在浏览器 localStorage 中，不同用户互不影响。

也可在 `fastapi-ai/.env` 中配置默认 Key：

```env
DEEPSEEK_API_KEY=sk-your-key
EMBEDDING_API_KEY=sk-your-key
```

### 3. 安装 & 启动

```bash
# FastAPI（先启动）
cd fastapi-ai
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# SpringBoot
cd springboot-backend
mvn spring-boot:run

# 前端
cd frontend
npm install && npm run dev
```

或 Windows 下双击 `start-all.bat` 一键启动。

### 4. 访问

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| SpringBoot API | http://localhost:8080 |
| FastAPI Docs | http://localhost:8000/docs |

## 功能模块

### 登录

![image-20260526105643266](imgs\image-20260526105643266.png)

### 首页

项目入口，提供「智能刷题」和「AI 带学」两个路径。右上角齿轮图标可配置 API Key。

![image-20260526105811721](imgs\image-20260526105811721.png)

### 智能刷题

三种模式：随机刷题、顺序刷题（支持分类筛选）、刷错题。选择题/判断题自动判题，问答题支持自主判题和 AI 判题两种方式。

AI 判题流程：规则预判 → LLM 语义分析 → Neo4j 知识点补全 → 学习路径生成。

![image-20260526105832845](imgs\image-20260526105832845.png)

### AI 带学（核心亮点）

基于 **Plan-and-Execute + Reflection + ReAct** 复合 Agent 范式：

```
选定 PDF → AI 通读全文提炼知识点 → 规划学习路径（Plan）
  → 逐知识点讲解 → 出题验证（Execute）
  → 语义评分 + 错因分析 → 决策前进/巩固/回退（Reflection）
  → 推理薄弱点 → 调整路径 → 再观察（ReAct 循环）
  → 全节点完成后自动生成综合测试
  → 根据掌握度决定结业或重新规划（RePlan）
```

支持断点续学：退出后自动恢复进度，答题中的题目精确还原。

![image-20260526105920135](imgs\image-20260526105920135.png)

![image-20260526105938785](imgs\image-20260526105938785.png)

### PDF 导入

上传 PDF → PDFBox 提取文本 → 分块 → FastAPI LangChain ChatPromptTemplate 提取 Q&A 对 → 去重入库。

![image-20260526105849755](imgs\image-20260526105849755.png)

### API Key 管理

前端任意页面的齿轮图标均可配置。Key 按请求隔离：每个用户浏览器的 localStorage 独立存储，通过 `X-Api-Key` 请求头传递，后端正则表达式过滤器 + FastAPI 中间件确保不同用户的 Key 互不干扰。

![image-20260526110020863](imgs\image-20260526110020863.png)

## API 接口

统一响应格式：`{"code": 200, "message": "success", "data": {...}}`

### 题库

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/questions?page=&size=` | 分页列表 |
| GET | `/api/questions/{id}` | 题目详情 |
| GET | `/api/questions/random` | 随机一题 |
| GET | `/api/questions/next?currentId=&topic=` | 下一题 |
| GET | `/api/questions/prev?currentId=&topic=` | 上一题 |
| GET | `/api/questions/count` | 总数 |
| GET | `/api/questions/topics` | 全部分类 |
| GET | `/api/questions/incorrect?userId=` | 错题列表 |
| DELETE | `/api/questions/{id}` | 删除 |

### 练习

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/practice/submit` | 提交答案 |
| PUT | `/api/practice/{id}/self-judge` | 自主判题 |
| PUT | `/api/practice/{id}/status` | 更新状态 |
| POST | `/api/practice/{id}/ai-analysis` | AI 分析 |
| GET | `/api/practice/records` | 练习记录 |
| GET | `/api/practice/stats` | 统计数据 |

### AI 带学

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/learn/plan` | 生成学习路径 |
| GET | `/api/learn/progress?pdfImportId=` | 获取进度 |
| GET | `/api/learn/progress-list` | 进度列表 |
| POST | `/api/learn/submit` | 提交答案（含 Reflection） |
| POST | `/api/learn/mark-learned` | 标记学会（返回匹配题目） |
| POST | `/api/learn/generate-test` | 生成综合测试 |
| POST | `/api/learn/evaluate-test` | 评估测试结果 |
| DELETE | `/api/learn/progress/{pdfImportId}` | 删除学习记录 |

### PDF 导入

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/pdf/upload` | 上传 PDF |
| GET | `/api/pdf/imports` | 导入历史 |
| DELETE | `/api/pdf/imports/{id}` | 删除 |

### 配置

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/config/api-key` | 查看 Key 状态 |
| POST | `/api/config/api-key` | 更新 Key |

## 数据库

MySQL 8，库名 `smartlearn`。5 张表：`users`, `questions`, `practice_records`, `pdf_imports`, `learn_progress`。DDL 见 `springboot-backend/src/main/resources/db/schema.sql`。

## 配置参考

| 配置文件 | 说明 |
|----------|------|
| `fastapi-ai/.env` | LLM/Embedding/Neo4j/Chroma 参数 |
| `springboot-backend/src/main/resources/application.yml` | MySQL、AI 地址、上传路径 |
| `frontend/vite.config.js` | 开发代理 `/api` → `localhost:8080` |

## 生产部署

CentOS 7.6 部署指南 → [`deploy/DEPLOY.md`](deploy/DEPLOY.md)

一键部署脚本 → `deploy/deploy.sh`
