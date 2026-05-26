# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Three-tier architecture

```
Vue 3 :5173 → SpringBoot :8080 → FastAPI :8000 → DeepSeek LLM + Neo4j + Chroma
用户前端         业务后端              AI 服务层       外部依赖
```

- **Frontend** (`frontend/`) — Vue 3 + Element Plus + Vite, dev server proxied to SpringBoot
- **Business backend** (`springboot-backend/`) — Spring Boot 2.7.18 + MyBatis + Lombok, Java 8
- **AI service** (`fastapi-ai/`) — FastAPI + DeepSeek + LangChain + Neo4j knowledge graph + Chroma vector DB

Frontend never calls FastAPI directly; SpringBoot is the single backend gateway. The bridge is `AiServiceClient` (SpringBoot → FastAPI HTTP client using `RestTemplate`).

Companion doc: `flowchart.md` — detailed 6-layer data flow diagram for the AI judging pipeline.

## Key constraints

- **Java 8 only** — no `var`, no switch expressions, no records, no `jakarta.*` (use `javax.*`), no `RestClient` (use `RestTemplate`)
- **MyBatis annotations** — no XML mapper files, all SQL is `@Select`/`@Insert`/`@Delete` on interface methods
- **GBK encoding bug** — Python `print()` with Chinese chars crashes on Windows GBK console. Never add debug prints to FastAPI code.
- **`parse_llm_json()`** in `fastapi-ai/app/core/utils.py` — the single JSON extraction utility used by all LLM-calling code. Uses `str.find()` (not `str.index()`) for closing backtick markers because LLM may not output them. Falls back: direct `json.loads` → extract ` ```json ``` ` → extract ` ``` ``` ` → return `{}`.
- **Lombok** — entity classes use `@Data`, `@NoArgsConstructor`, `@AllArgsConstructor`. Do not write manual getters/setters.

## Start / build commands

```bash
# FastAPI (start first — SpringBoot depends on it)
cd fastapi-ai
uvicorn app.main:app --host 0.0.0.0 --port 8000

# SpringBoot
cd springboot-backend
mvn spring-boot:run

# Vue frontend
cd frontend
npm run dev

# One-click (Windows only — opens 3 terminal windows)
./start-all.bat
```

**Warning:** `start-all.bat` runs `taskkill /F /IM java.exe`, `python.exe`, and `node.exe` globally before starting — it will kill all unrelated Java/Python/Node processes on the machine.

There are no automated tests in this project.

## API contract

All responses follow: `{"code": 200, "message": "success", "data": {...}}`.
The frontend axios interceptor (`frontend/src/api/client.js`) strips this envelope — calls return `data.data` directly.
Error responses from SpringBoot set code ≠ 200; the interceptor throws with `data.message`.

FastAPI responses are plain JSON (no envelope) consumed by SpringBoot's `AiServiceClient`, which wraps them in the envelope before returning to the frontend.

## Auth system

JWT-based authentication via `AuthController` (`/api/auth/*`).

- **Register** `POST /api/auth/register` — username + password (≥6 chars) + optional nickname. Password hashed with SHA-256 (not bcrypt for the stored hash; the default admin user uses bcrypt in the SQL seed but runtime uses SHA-256).
- **Login** `POST /api/auth/login` — returns JWT token + user info. Frontend stores token in `localStorage.sm_token`.
- **Me** `GET /api/auth/me` — returns current user from JWT via `UserContext.getUserId()`.

Frontend: `LoginPage.vue` is the only non-auth-gated route. Router guard in `router/index.js` checks `isLoggedIn()` and redirects to `/login`. The axios interceptor in `client.js` attaches the JWT as `Authorization: Bearer <token>` header.

JWT config: `springboot-backend/.../config/JwtUtil.java`. Secret is hardcoded for dev. Token expiry: 7 days.

## Config / API Key management

Users bring their own DeepSeek API key, stored in `localStorage.sm_ds_key` on the frontend. The key flows through two layers:

1. **Frontend** → `SettingsModal.vue` + `configApi.js` → `PUT /api/config/api-key` to SpringBoot
2. **SpringBoot** `ConfigController` → proxies to FastAPI `POST /api/config/api-key` (stores key in memory via `llm_service`)
3. **Per-request** — frontend sends `X-Api-Key` header with every request; SpringBoot's `ApiKeyHolder` reads it in a filter; `AiServiceClient` forwards it to FastAPI; FastAPI's `per_request_api_key` middleware sets it on `llm_service` for that request only.

Clearing the key: `DELETE /api/config/api-key` → removes from both localStorage and FastAPI memory. On logout, the key is cleared automatically.

FastAPI endpoints (defined in `main.py`, not a separate router):
- `GET /api/config/api-key` — get masked key status
- `POST /api/config/api-key` — set key
- `DELETE /api/config/api-key` — clear key

## SpringBoot API endpoints

### Questions
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/questions?page=&size=` | Paginated question list |
| `GET` | `/api/questions/{id}` | Single question |
| `GET` | `/api/questions/random` | Random question (optionally filtered by userId) |
| `GET` | `/api/questions/next?currentId=&topic=` | Next question (topic-filtered or global) |
| `GET` | `/api/questions/prev?currentId=&topic=` | Previous question |
| `GET` | `/api/questions/count` | Total question count |
| `GET` | `/api/questions/topics` | All distinct topics |
| `GET` | `/api/questions/incorrect?userId=` | User's incorrect questions |
| `DELETE` | `/api/questions/{id}` | Delete a question |

### Practice
| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/practice/submit` | Submit answer → triggers AI analysis flow |
| `PUT` | `/api/practice/{id}/self-judge` | Self-judge (mark correct/incorrect manually) |
| `PUT` | `/api/practice/{id}/status` | Update practice record status |
| `GET` | `/api/practice/records?userId=&status=&page=&size=` | Practice history |
| `GET` | `/api/practice/stats?userId=` | User practice stats |
| `POST` | `/api/practice/{id}/ai-analysis` | Re-run AI analysis on existing record |

### PDF Import
| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/pdf/upload` | Upload PDF for Q&A extraction |
| `GET` | `/api/pdf/imports?userId=` | PDF import history |
| `GET` | `/api/pdf/status/{id}` | PDF import progress |

### AI Guided Learning ("AI 带学")
| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/learn/plan` | Generate learning plan from PDF questions |
| `GET` | `/api/learn/progress?pdfImportId=` | Get learning progress for a PDF |
| `GET` | `/api/learn/progress-list` | List all learning progress for current user |
| `POST` | `/api/learn/submit` | Submit answer in learning session |
| `POST` | `/api/learn/mark-learned` | Mark a knowledge point as learned |
| `DELETE` | `/api/learn/progress/{pdfImportId}` | Delete learning progress |
| `POST` | `/api/learn/generate-test` | Generate comprehensive test from learned KPs |
| `POST` | `/api/learn/evaluate-test` | Evaluate test, decide pass/re-plan |

### Auth
| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | Login, get JWT |
| `GET` | `/api/auth/me` | Get current user info |

### Config
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/config/api-key` | Get API key status (masked) |
| `POST` | `/api/config/api-key` | Set DeepSeek API key |
| `DELETE` | `/api/config/api-key` | Clear API key |

## FastAPI routes

| Prefix | Module | Called by |
|--------|--------|-----------|
| `/api/analysis/*` | `analysis.py` | SpringBoot (practice submit → AI judging) |
| `/api/pdf/*` | `pdf_parse.py` | SpringBoot (PDF Q&A extraction) |
| `/api/learn/*` | `learning_agent.py` | SpringBoot (AI guided learning agent) |
| `/api/rag/*` | `rag.py` | Streamlit / direct (RAG Q&A) |
| `/api/knowledge/*` | `knowledge.py` | Admin / direct (KG CRUD) |
| `/api/learning-path/*` | `learning_path.py` | Direct (learning path generation) |
| `/api/config/api-key` | `main.py` | SpringBoot (API key CRUD, proxied via ConfigController) |
| `GET /api/health` | `main.py` | Health check |

## SpringBoot service layer

| Service | Purpose |
|---------|---------|
| `QuestionService` | Question CRUD, random/next/prev navigation, topic listing |
| `PracticeService` | Practice submission, self-judge, status updates, AI analysis orchestration |
| `PdfImportService` | PDF upload, chunk-based LLM extraction, dedup & insert |
| `LearnService` | Learning plan generation, progress tracking, test generation & evaluation |

## FastAPI service layer

| Service | Purpose |
|---------|---------|
| `llm_service` | DeepSeek model factory, API key management (in-memory store + per-request override) |
| `analysis_service` | Rule-based judge + LLM deep analysis + Neo4j enrichment + learning path |
| `pdf_parse_service` | LLM Q&A extraction from PDF text chunks |
| `kg_service` | Neo4j driver, knowledge graph queries, prerequisite chain traversal |
| `path_service` | Learning path tracing through PREREQUISITE edges in Neo4j |
| `rag_service` | Hybrid retrieval (vector + keyword), LLM answer generation with context |
| `vector_service` | Chroma vector DB operations (add, search, delete) |
| `embedding_service` | Text embedding via DeepSeek API |
| `rerank_service` | Result re-ranking for RAG quality |

## Frontend architecture

6 views, organized into component subtrees:

```
AppLayout (layout shell with nav)
  LoginPage              — standalone, no auth required
  HomePage               — dashboard / landing
  PracticePage           — core quiz interface
    QuestionCard
      ChoiceOptionList
      FillBlankInput
    ActionBar
    ModeSelector         — "self-judge" vs "AI judge" toggle
    JudgeModeDialog      — post-answer result + trigger AI analysis
    SelfJudgePanel
    AiAnalysisPanel
      ErrorAnalysisDisplay
      WeakPointsList
      LearningPathTimeline
    ProgressSidebar
    NavigationControls
  PdfImportPage          — PDF upload & import management
    UploadDragger
    ImportHistoryTable
    ImportResultModal
  LearnHubPage           — AI guided learning hub (list active learning sessions)
  LearnSessionPage       — active learning session (Plan-Execute-Reflection-RePlan)
    SessionTopBar
    ExplainView          — knowledge point teaching content
    QuizView             — question answering with AI semantic judge
    ReflectionLog        — session history & reflection
    PathTimeline         — learning path progress timeline
  SettingsModal (common) — API key config, overlay on all pages
```

- State lives in each view component — no Vuex/Pinia store.
- `ModeSelector` switches between "self-judge" and "AI judge" modes.
- `JudgeModeDialog` appears after answering — shows result and triggers AI analysis if applicable.

## Frontend API layer (`frontend/src/api/`)

| Module | Purpose |
|--------|---------|
| `client.js` | Axios instance: base URL from env, attaches JWT `Authorization` header, attaches `X-Api-Key` from localStorage, strips response envelope |
| `authApi.js` | Login, register, me, token helpers (`getToken`/`setToken`/`removeToken`/`isLoggedIn`/`logout`) |
| `questionApi.js` | Question list, detail, random, next/prev, count, topics, delete |
| `practiceApi.js` | Submit answer, self-judge, status update, records, stats, re-run AI analysis |
| `pdfApi.js` | PDF upload, import history, import status |
| `learnApi.js` | Learning plan, progress, submit answer, mark learned, generate/evaluate test. Has `USE_MOCK` flag for offline dev — mock data simulates the full Plan-Execute-Reflection-RePlan loop. |
| `configApi.js` | Get/set/clear DeepSeek API key |

## Database

MySQL 8, schema `smartlearn`, user `root` / password `666666`.

5 tables: `users`, `questions`, `practice_records`, `pdf_imports`, `learn_progress`.
DDL at `springboot-backend/src/main/resources/db/schema.sql`.

- `users` — JWT auth. Default admin: `admin` / `admin123`. Passwords hashed with SHA-256 at runtime (the seed INSERT uses bcrypt for the default user but runtime `AuthController` uses SHA-256).
- `learn_progress` — stores the full learning path JSON, current node index/state, completed nodes, reflection log, quiz history. One row per user+pdfImport pair.

## AI judging flow (the core diagnostic pipeline)

When `judgeMode = "ai"`:
1. **Rule-based judge** — Python compares answers locally (not LLM). Exact match for choice/true-false, contains-match for essay.
2. **LLM deep analysis** — DeepSeek generates error analysis + weak point assessment (mastery 0.0-1.0 per knowledge point)
3. **Neo4j enrichment** — `_enrich_weak_points()` in `analysis_service.py` queries Neo4j for official knowledge point names, combines with LLM's mastery scores
4. **Learning path** — `path_service.py` traces PREREQUISITE chain in Neo4j, then LLM writes 1-sentence study tips for each node

The knowledge graph (`fastapi-ai/scripts/java_knowledge_graph.json`) has 693 nodes / 2,354 edges across 54 categories. Build scripts: `build_kg.py` (from JSON), `enrich_relations.py` (LLM infers relations).

See `flowchart.md` for the full 6-layer data flow with Mermaid diagram.

## AI Guided Learning flow ("AI 带学")

A Plan-Execute-Reflection-RePlan loop for studying PDF-imported question banks:

1. **Generate Plan** — User picks a PDF import → SpringBoot sends all its questions to FastAPI `POST /api/learn/generate-plan` → LLM reads all questions, distills them into 5-15 knowledge points ordered basic→advanced, writes teaching outlines, and maps questions to KPs. Stored in `learn_progress.learning_path_json`.
2. **Execute** — Frontend walks the learning path node by node. Each node has two states:
   - `explain` — `ExplainView` shows the KP's teaching content
   - `quiz` — `QuizView` presents a question from that KP; user answers → FastAPI `POST /api/learn/submit-answer` does AI semantic judging (choice questions: exact match; essay/fill-blank: LLM scores 0.0-1.0 with detailed feedback). Score ≥ 0.85 → advance; < 0.85 → reinforce (get another question on same KP).
3. **Reflection** — `ReflectionLog` shows session history. User can mark a KP as learned → `POST /api/learn/mark-learned`.
4. **Test** — After all KPs learned → `POST /api/learn/generate-test` → LLM selects representative questions across all KPs.
5. **Evaluate** — `POST /api/learn/evaluate-test` → LLM scores overall mastery. If below threshold (default 0.7), generates a new learning path targeting weak points → back to step 2.

`learnApi.js` has a `USE_MOCK` flag that simulates this entire flow without backend — useful for frontend-only development.

## PDF import pipeline

1. PDFBox extracts raw text (streaming, not memory-bound)
2. Text split into 5,000-char chunks at page markers (`"No. X / N"`) or newline boundaries
3. Each chunk → FastAPI `POST /api/pdf/parse-qa` → DeepSeek extracts Q&A pairs as JSON
4. SpringBoot deduplicates by first-50-chars of content, inserts into `questions` table
5. Frontend polls `chunks_completed / total_chunks` for progress bar

All timeouts are 600s (10 min) — LLM calls for large PDFs are slow.

## Important configuration files

- `fastapi-ai/.env` — **Must configure.** Needs `DEEPSEEK_API_KEY` and `EMBEDDING_API_KEY`. Neo4j credentials, Chroma path, RAG params.
- `springboot-backend/src/main/resources/application.yml` — MySQL, AI base URL, upload path. Has defaults.
- `frontend/vite.config.js` — Dev proxy `/api` → `localhost:8080`. No .env needed.

## Neo4j

Server: `134.175.252.240:7687`, user `neo4j`, password `Neo4j123456`.
Knowledge points use `MERGE` on `id` — re-running build scripts is idempotent.
If the knowledge graph has no nodes, run `cd fastapi-ai && python scripts/build_java_kg.py`.
