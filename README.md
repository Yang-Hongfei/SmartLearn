# SmartLearn 智能刷题平台

基于 **知识图谱 + RAG** 的个性化算法学习平台，为每位学习者动态规划专属学习路径。

## 项目概述

SmartLearn 从《算法导论》等经典教材中提取核心概念，构建包含 500+ 知识点与 2000+ 条关系的算法知识图谱，采用**向量检索 + 关键词检索**的混合 RAG 策略实现智能答疑，并根据用户答题情况自动分析薄弱点，结合知识图谱关联关系动态生成个性化学习路径（如从"递归"→"分治法"→"动态规划"）。

### 核心特性

- **知识图谱驱动** — Neo4j 存储知识点层级与前置依赖关系，支持图算法路径规划
- **混合 RAG 检索** — 向量语义检索 + 关键词匹配，Cohere Rerank 重排序提升准确率
- **答题智能诊断** — 接收题目+用户答案，自动判题并生成错题解析、薄弱点分析、学习路径
- **个性化学习路径** — 根据薄弱点+图遍历自动规划最优学习顺序，LLM 生成学习建议
- **零额外部署** — Chroma 嵌入式模式本地运行，无需独立向量数据库服务

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **后端框架** | SpringBoot + MyBatis | 业务后端：用户系统、题库管理、答题记录 |
| **AI 服务层** | FastAPI (Python 3.12) | AI 中台：RAG、知识图谱、学习路径、答题诊断 |
| **LLM** | Qwen-Max（阿里云百炼） | 知识抽取、RAG 生成、错题解析、学习建议 |
| **Embedding** | text-embedding-v4（百炼） | 文本向量化，1024 维 |
| **向量数据库** | Chroma（嵌入式模式） | 本地文件持久化，余弦相似度检索 |
| **图数据库** | Neo4j Community | 知识图谱存储、图遍历、最短路径查询 |
| **Rerank** | Cohere Rerank（可选） | 多语言重排序，未配置时自动跳过 |
| **关系型数据库** | MySQL + Redis | 用户数据、题库缓存 |
| **AI 前端** | Streamlit | AI 功能可视化调试面板 |
| **用户前端** | React + Ant Design + Monaco Editor + AntV G6 | 交互式学习界面 |

## 项目结构

```
SmartLearn智能刷题平台/
├── fastapi-ai/                          # AI 服务层（本项目主体）
│   ├── app/
│   │   ├── main.py                      # FastAPI 入口，路由注册 + CORS
│   │   ├── core/
│   │   │   ├── config.py                # pydantic-settings 配置管理
│   │   │   └── utils.py                 # 共享工具（JSON解析、关键词提取、去重合并）
│   │   ├── api/
│   │   │   ├── analysis.py              # SpringBoot 对接核心：答题诊断
│   │   │   ├── rag.py                   # RAG 智能问答
│   │   │   ├── knowledge.py             # 知识图谱 CRUD + 路径查询
│   │   │   └── learning_path.py         # 学习路径规划
│   │   ├── services/
│   │   │   ├── analysis_service.py      # 错题解析 + 薄弱点诊断 + 路径生成
│   │   │   ├── llm_service.py           # Qwen-Max 调用（DashScope OpenAI 兼容 API）
│   │   │   ├── embedding_service.py     # Qwen3-Embedding 向量化
│   │   │   ├── vector_service.py        # Chroma 向量检索（langchain_chroma）
│   │   │   ├── kg_service.py            # Neo4j 图数据库 CRUD + 路径查询
│   │   │   ├── rerank_service.py        # Cohere Rerank 重排序（含降级处理）
│   │   │   ├── rag_service.py           # 混合检索 RAG 编排
│   │   │   └── path_service.py          # 学习路径规划 + LLM 建议生成
│   │   └── models/
│   │       └── schemas.py               # Pydantic 请求/响应模型
│   ├── scripts/
│   │   ├── build_kg.py                  # 知识图谱构建（JSON 导入 / LLM 抽取）
│   │   ├── ingest_docs.py               # 文档向量化入库
│   │   └── sample_knowledge_points.json # 示例：30 知识点 + 37 条关系
│   ├── springboot-example/
│   │   └── RagClient.java               # SpringBoot RestClient 调用示例
│   ├── streamlit_app.py                 # Streamlit AI 可视化前端
│   ├── docker-compose.yml               # Neo4j 一键部署
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── springboot-backend/                  # SpringBoot 业务后端（独立开发）
└── frontend/                            # React 用户前端（独立开发）
```

## SpringBoot ↔ FastAPI 数据流

```
SpringBoot                          FastAPI
─────────                          ───────
发送：题目 + 用户答案    ──→   POST /api/analysis/submit-answer
                                    │
                                    ├── 基础判题（对/错）
                                    ├── LLM 深度分析错误原因
                                    ├── 知识点掌握度评估
                                    ├── Neo4j 图遍历规划路径
                                    └── LLM 生成学习建议
                                    │
返回：JSON                  ←──      错题解析
                                    薄弱点分析
                                    学习路径
```

## API 接口

### 核心接口：答题诊断

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/analysis/submit-answer` | **SpringBoot 对接核心**：提交题目+用户答案，返回错题解析+薄弱点+学习路径 |

**请求示例：**

```json
{
  "user_id": "spring_user_001",
  "question": {
    "id": "q_001",
    "type": "single_choice",
    "content": "动态规划的核心要素不包括以下哪个？",
    "options": ["A. 状态定义", "B. 状态转移方程", "C. 贪心选择性质", "D. 边界条件"],
    "correct_answer": "C",
    "knowledge_point_ids": ["kp_dp", "kp_greedy"],
    "difficulty": 3
  },
  "user_answer": "B"
}
```

**返回示例：**

```json
{
  "user_id": "spring_user_001",
  "question_id": "q_001",
  "is_correct": false,
  "error_analysis": {
    "user_answer": "B",
    "correct_answer": "C",
    "explanation": "动态规划的核心要素包括状态定义、状态转移方程和边界条件...",
    "error_type": "概念混淆",
    "error_detail": "学生选了状态转移方程，混淆了DP与贪心算法的贪心选择性质"
  },
  "weak_point_analysis": [
    {
      "knowledge_point_id": "kp_dp",
      "knowledge_point_name": "动态规划",
      "current_mastery": 0.6,
      "reason": "对DP与贪心的区别理解不够清晰"
    }
  ],
  "learning_path": [
    {
      "order": 1,
      "knowledge_point": {"id": "kp_greedy", "name": "贪心算法", ...},
      "reason": "先学贪心选择性质，区分与DP的不同..."
    }
  ],
  "generated_at": "2026-05-09T17:34:33"
}
```

### 其他接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/health` | 健康检查 |
| `POST` | `/api/rag/query` | RAG 智能问答 |
| `POST` | `/api/knowledge/search` | 搜索知识点 |
| `GET` | `/api/knowledge/point/{id}` | 查询单个知识点 |
| `GET` | `/api/knowledge/point/{id}/related` | 查询关联知识点 |
| `POST` | `/api/knowledge/path` | 两知识点间最短路径 |
| `POST` | `/api/knowledge/relation` | 创建知识点关系 |
| `GET` | `/api/knowledge/categories` | 获取所有知识点分类 |
| `POST` | `/api/learning-path/generate` | 生成个性化学习路径 |

### SpringBoot 调用示例

```java
// 注入 AiServiceClient
AiServiceClient.AnswerAnalysisResponse result = aiServiceClient.submitAnswer(
    userId,           // "spring_user_001"
    questionId,       // "q_001"
    "single_choice",  // 题型
    questionContent,  // 题目文本
    options,          // String[]{"A. ...", "B. ...", ...}
    "C",              // 正确答案
    "B",              // 用户答案
    kpIds,            // String[]{"kp_dp", "kp_greedy"}
    3                 // 难度
);

if (!result.is_correct()) {
    // 展示 result.error_analysis() 给用户
    // 根据 result.weak_point_analysis() 更新用户画像
    // 推荐 result.learning_path() 给用户
}
```

## 快速开始

### 前置条件

- Python 3.10+
- Neo4j（远程服务器 或 Docker 本地部署）

### 1. 安装依赖

```bash
cd fastapi-ai
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`：

```env
# 必填：阿里云百炼 API Key
DASHSCOPE_API_KEY=sk-your-key

# 必填：Neo4j 连接
NEO4J_URI=bolt://your-server:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# 可选：Cohere Rerank（不填自动跳过）
COHERE_API_KEY=your-cohere-key
```

### 3. 启动 Neo4j（如无远程服务）

```bash
docker-compose up -d
```

或下载 [Neo4j Desktop](https://neo4j.com/download/) 一键启动。

### 4. 构建知识图谱

```bash
python scripts/build_kg.py --input scripts/sample_knowledge_points.json
```

### 5. 启动 AI 服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 [http://localhost:8000/docs](http://localhost:8000/docs) 查看 Swagger 文档。

### 6. 启动 Streamlit 可视化前端

```bash
streamlit run streamlit_app.py
```

访问 [http://localhost:8501](http://localhost:8501) 打开 AI 功能调试面板。

## RAG Pipeline

```
用户提问
  │
  ├─→ Qwen3-Embedding 向量化 (1024d)
  │
  ├─→ Chroma 向量检索 (top_k × 2)
  │     └─→ 关键词检索（补充召回）
  │
  ├─→ merge_dedup 合并去重
  │
  ├─→ Cohere Rerank 重排序（可选，未配置时跳过）
  │
  ├─→ 构建 System Prompt + 上下文拼接
  │
  └─→ Qwen-Max 生成答案 + 引用标注
```

## 知识图谱结构

```
递归 ──PREREQUISITE──→ 分治法 ──PREREQUISITE──→ 动态规划
  │                        │                        │
  ├──→ DFS                  └──→ 快速排序            ├──→ 背包问题
  ├──→ 回溯法                   归并排序            ├──→ 最长公共子序列
  ├──→ 记忆化搜索                                    └──→ 最长递增子序列
  └──→ 二叉树
```

## 服务端口

| 服务 | 地址 | 用途 |
|------|------|------|
| FastAPI | `http://localhost:8000` | AI 接口服务 |
| Swagger | `http://localhost:8000/docs` | API 文档 |
| Streamlit | `http://localhost:8501` | AI 可视化前端 |
| Neo4j Browser | `http://localhost:7474` | 图数据库管理 |

## 流程可视化

