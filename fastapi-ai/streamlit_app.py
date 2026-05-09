"""
SmartLearn AI — Streamlit 前端
四个模块：答题分析 / RAG问答 / 知识图谱 / 学习路径
"""
import httpx
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(
    page_title="SmartLearn AI", page_icon="🧠", layout="wide",
    initial_sidebar_state="expanded",
)

API = "http://localhost:8000"
CATEGORY_COLORS = {
    "算法思想": "#6366F1", "数据结构": "#22C55E", "搜索": "#F97316",
    "排序": "#EC4899", "图论": "#06B6D4", "动态规划": "#8B5CF6",
    "算法技巧": "#EAB308", "基础概念": "#3B82F6",
}

# ==================== 工具函数 ====================

def api_get(path: str):
    try:
        r = httpx.get(f"{API}{path}", timeout=10.0)
        return r.json() if r.status_code == 200 else {"error": r.text}
    except Exception as e:
        return {"error": str(e)}


def api_post(path: str, body: dict, timeout: int = 90):
    try:
        r = httpx.post(f"{API}{path}", json=body, timeout=timeout)
        return r.json() if r.status_code == 200 else {"error": r.text}
    except Exception as e:
        return {"error": str(e)}


def kp_color(category: str) -> str:
    return CATEGORY_COLORS.get(category, "#999999")


def stars(n: int) -> str:
    return "⭐" * n


# ==================== 侧边栏 ====================

with st.sidebar:
    st.title("🧠 SmartLearn AI")
    st.caption("基于知识图谱 + RAG 的智能学习平台")

    health = api_get("/api/health")
    if health.get("status") == "ok":
        st.success("🟢 AI 服务已连接")
    else:
        st.error("🔴 服务离线")

    st.divider()
    st.subheader("📖 知识点分类")
    cats = api_get("/api/knowledge/categories")
    if isinstance(cats, list):
        cols = st.columns(2)
        for i, cat in enumerate(cats):
            color = kp_color(cat)
            cols[i % 2].markdown(f":{color}[●] {cat}")

    st.divider()
    st.caption("Qwen-Max · Chroma · Neo4j · Cohere")
    st.caption("FastAPI :8000 | Streamlit :8501")


# ==================== 主区域 ====================

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 答题分析", "💬 RAG 问答", "🔗 知识图谱", "🗺️ 学习路径",
])

# ==================== Tab 1: 答题分析 ====================

with tab1:
    st.subheader("📝 答题诊断")
    st.caption("模拟 SpringBoot 调用：提交题目 + 用户答案 → 返回错题解析 + 薄弱点 + 学习路径")

    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("**📋 题目信息**")
        q_type = st.selectbox("题型", ["single_choice", "fill_blank", "true_false"])
        q_content = st.text_area(
            "题目内容", value="动态规划的核心要素不包括以下哪个？", height=100,
        )
        if q_type == "single_choice":
            options_raw = st.text_area("选项（每行一个）", value="A. 状态定义\nB. 状态转移方程\nC. 贪心选择性质\nD. 边界条件", height=100)
            options = [o.strip() for o in options_raw.split("\n") if o.strip()]
        else:
            options = None

        correct = st.text_input("正确答案", value="C")
        kp_ids_raw = st.text_input("关联知识点ID（逗号分隔）", value="kp_dp, kp_greedy")
        kp_ids = [k.strip() for k in kp_ids_raw.split(",") if k.strip()]
        difficulty = st.slider("难度", 1, 5, 3)

        st.markdown("**👤 用户答案**")
        user_answer = st.text_input("用户答案", value="B", key="user_ans")

        if st.button("🚀 提交分析", type="primary", use_container_width=True):
            with st.spinner("AI 分析中..."):
                resp = api_post("/api/analysis/submit-answer", {
                    "user_id": "demo_user",
                    "question": {
                        "id": f"q_demo_{q_type}",
                        "type": q_type,
                        "content": q_content,
                        "options": options,
                        "correct_answer": correct,
                        "knowledge_point_ids": kp_ids,
                        "difficulty": difficulty,
                    },
                    "user_answer": user_answer,
                }, timeout=120)
            st.session_state.analysis_result = resp
        else:
            if "analysis_result" not in st.session_state:
                # Demo data
                st.session_state.analysis_result = api_post("/api/analysis/submit-answer", {
                    "user_id": "demo",
                    "question": {
                        "id": "q_demo", "type": "single_choice",
                        "content": "动态规划的核心要素不包括以下哪个？",
                        "options": ["A. 状态定义", "B. 状态转移方程", "C. 贪心选择性质", "D. 边界条件"],
                        "correct_answer": "C",
                        "knowledge_point_ids": ["kp_dp", "kp_greedy"],
                        "difficulty": 3,
                    },
                    "user_answer": "B",
                }, timeout=120)

    with c2:
        result = st.session_state.get("analysis_result", {})
        if result.get("is_correct") is not None:
            is_correct = result["is_correct"]
            st.markdown(
                f"## {'✅ 回答正确！' if is_correct else '❌ 回答错误'}"
            )
            st.caption(
                f"生成时间: {result.get('generated_at', '')}"
            )

            # 错题解析
            st.divider()
            if result.get("error_analysis"):
                st.subheader("🔍 错题解析")
                ea = result["error_analysis"]
                st.info(f"**错误类型**: {ea.get('error_type', '')}")
                st.markdown(f"**题目解析**\n{ea.get('explanation', '')}")
                st.warning(f"**错误原因**\n{ea.get('error_detail', '')}")
            else:
                st.success("继续加油！这道题已掌握。")

            # 薄弱点
            st.divider()
            st.subheader("📊 薄弱点分析")
            for wp in result.get("weak_point_analysis", []):
                mastery = wp["current_mastery"]
                pct = int(mastery * 100)
                bar_color = (
                    "#22c55e" if pct >= 70 else "#f97316" if pct >= 40 else "#ef4444"
                )
                st.markdown(f"**{wp['knowledge_point_name']}**")
                st.progress(mastery)
                st.caption(f"掌握度 {pct}% — {wp['reason'][:100]}")
                st.markdown("---")

            # 学习路径
            lp_nodes = result.get("learning_path", [])
            if lp_nodes:
                st.divider()
                st.subheader("🗺️ 学习路径")
                snodes, sedges, prev = [], [], None
                for node in lp_nodes:
                    kp = node["knowledge_point"]
                    c = kp_color(kp.get("category", ""))
                    snodes.append(Node(
                        id=kp["id"], label=kp["name"], size=25, color=c,
                        title=kp.get("description", ""),
                    ))
                    if prev:
                        sedges.append(Edge(source=prev, target=kp["id"]))
                    prev = kp["id"]

                if snodes:
                    agraph(nodes=snodes, edges=sedges, config=Config(
                        width=500, height=200, directed=True,
                        physics=False, hierarchical=True, direction="LR",
                        nodeSpacing=120, levelSeparation=120,
                    ))

                for node in lp_nodes:
                    kp = node["knowledge_point"]
                    st.markdown(
                        f"{node['order']}. **{kp['name']}** — {node['reason'][:80]}"
                    )

        elif "error" in result:
            st.error(result["error"])


# ==================== Tab 2: RAG 问答 ====================

with tab2:
    c_left, c_right = st.columns([3, 1])

    with c_left:
        st.subheader("🤖 智能答疑")

        if "rag_msgs" not in st.session_state:
            st.session_state.rag_msgs = []

        for msg in st.session_state.rag_msgs:
            with st.chat_message(msg["role"], avatar=msg["avatar"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("📚 参考资料"):
                        for i, src in enumerate(msg["sources"], 1):
                            score = src.get("score", 0)
                            sc = "green" if score > 0.7 else "orange" if score > 0.4 else "gray"
                            st.caption(f"[{i}] {src.get('title','')} — :{sc}[{score:.2f}]")
                            st.markdown(f"> {src.get('content_snippet','')}")

        if q := st.chat_input("输入你的算法问题..."):
            st.session_state.rag_msgs.append({"role": "user", "content": q, "avatar": "👤", "sources": []})
            with st.chat_message("user", avatar="👤"):
                st.markdown(q)
            with st.chat_message("assistant", avatar="🧠"):
                with st.spinner("检索中..."):
                    resp = api_post("/api/rag/query", {"question": q, "top_k": 5}, timeout=90)
                if "error" in resp:
                    st.error(resp["error"])
                else:
                    st.markdown(resp["answer"])
                    sources = resp.get("sources", [])
                    if sources:
                        with st.expander("📚 参考资料"):
                            for i, src in enumerate(sources, 1):
                                sc = "green" if src["score"] > 0.7 else "orange" if src["score"] > 0.4 else "gray"
                                st.caption(f"[{i}] {src.get('title','')} — :{sc}[{src['score']:.2f}]")
                                st.markdown(f"> {src.get('content_snippet','')}")
                    if resp.get("related_knowledge_points"):
                        st.caption("🔗 " + " · ".join(resp["related_knowledge_points"]))
            st.session_state.rag_msgs.append({
                "role": "assistant", "content": resp.get("answer", ""),
                "avatar": "🧠", "sources": resp.get("sources", []),
            })

    with c_right:
        st.metric("问答轮次", len([m for m in st.session_state.rag_msgs if m["role"] == "user"]))
        with st.expander("⚙️ 检索 Pipeline"):
            st.markdown("""
            1. Qwen3-Embedding 向量化
            2. Chroma 向量检索 (top_k × 2)
            3. 关键词检索补充
            4. Cohere Rerank 重排
            5. Qwen-Max 生成答案
            """)
        if st.button("🗑️ 清空对话", key="clear_rag"):
            st.session_state.rag_msgs = []
            st.rerun()


# ==================== Tab 3: 知识图谱 ====================

with tab3:
    c_search, c_detail = st.columns([1, 2])

    with c_search:
        st.subheader("🔍 搜索")
        kw = st.text_input("关键词", placeholder="如：递归、排序...")
        cat = st.selectbox("分类", ["全部"] + list(CATEGORY_COLORS.keys()), index=0)

        if kw:
            results = api_post("/api/knowledge/search", {
                "keyword": kw,
                "category": cat if cat != "全部" else None,
                "limit": 15,
            })
            if isinstance(results, list):
                for kp in results:
                    c = kp_color(kp.get("category", ""))
                    with st.container(border=True):
                        st.markdown(f"**:{c}[●] {kp['name']}**")
                        st.caption(kp.get("description", ""))
                        st.caption(f"`{kp['id']}`  {stars(kp.get('difficulty', 1))}")
                        if st.button("查看详情", key=f"d_{kp['id']}"):
                            st.session_state.sel_kp = kp["id"]

    with c_detail:
        st.subheader("📋 详情")
        sel = st.session_state.get("sel_kp", "")
        if not sel:
            sel = st.text_input("知识点ID", placeholder="kp_recursion")

        if sel:
            kp = api_get(f"/api/knowledge/point/{sel}")
            if isinstance(kp, dict) and "id" in kp:
                c = kp_color(kp.get("category", ""))
                st.markdown(f"## :{c}[●] {kp['name']}")
                st.caption(f"{kp.get('category','')} | {stars(kp.get('difficulty',1))}")
                st.markdown(kp.get("description", ""))

                # 关联图谱
                related = api_get(f"/api/knowledge/point/{sel}/related")
                if isinstance(related, list) and related:
                    st.subheader("🔗 关联知识点")
                    nodes = [Node(id=kp["id"], label=kp["name"], size=40, color=c)]
                    edges = []
                    seen_edges = set()
                    for rel in related[:15]:
                        rid = rel.get("id", "")
                        rname = rel.get("name", rid)
                        rc = kp_color(rel.get("category", ""))
                        nodes.append(Node(id=rid, label=rname, size=30, color=rc))
                        rel_type = rel.get("relation", "")
                        label = "前置" if "PREREQUISITE" in rel_type else "相关"
                        key = (kp["id"], rid, label)
                        if key not in seen_edges:
                            seen_edges.add(key)
                            edges.append(Edge(source=kp["id"], target=rid, label=label))
                    agraph(nodes=nodes, edges=edges, config=Config(
                        width=700, height=400, directed=True, physics=True,
                        nodeHighlightBehavior=True, highlightColor="#F7A7A6",
                    ))
                    st.dataframe(
                        [{"知识点": r["name"], "分类": r.get("category",""), "关系": r.get("relation",""), "权重": r.get("weight",0)} for r in related],
                        use_container_width=True, hide_index=True,
                    )

                # 路径查询
                st.divider()
                st.subheader("🛤️ 路径查询")
                to_id = st.text_input("目标知识点ID", placeholder="kp_dp", key="path_to")
                if to_id and st.button("查找最短路径", key="find_path_btn"):
                    pr = api_post("/api/knowledge/path", {"from_id": sel, "to_id": to_id, "max_depth": 5})
                    nodes = pr.get("nodes", [])
                    if nodes:
                        st.success(f"路径: {' → '.join(n['name'] for n in nodes)}")
                        pn, pe = [], []
                        for i, n in enumerate(nodes):
                            pn.append(Node(id=n["id"], label=n["name"], size=25, color=kp_color(n.get("category",""))))
                            if i > 0:
                                pe.append(Edge(source=nodes[i-1]["id"], target=n["id"]))
                        agraph(nodes=pn, edges=pe, config=Config(
                            width=700, height=150, directed=True, physics=False, hierarchical=True,
                        ))
                    else:
                        st.warning("未找到路径")


# ==================== Tab 4: 学习路径 ====================

with tab4:
    st.subheader("🗺️ 个性化学习路径规划")

    c_in, c_out = st.columns([1, 2])

    with c_in:
        all_kps = api_post("/api/knowledge/search", {"keyword": "", "limit": 50})
        kp_opts = {}
        if isinstance(all_kps, list):
            for kp in all_kps:
                kp_opts[f"{kp['name']} ({kp['id']})"] = kp["id"]

        st.subheader("📝 薄弱知识点")
        num = st.number_input("数量", 1, 5, 2)
        weak_points = []
        for i in range(num):
            cols = st.columns([3, 1])
            with cols[0]:
                sel = st.selectbox(f"知识点 {i+1}", list(kp_opts.keys()), key=f"wp_{i}")
            with cols[1]:
                score = st.slider(f"掌握度", 0.0, 1.0, 0.3, 0.05, key=f"sc_{i}")
            if sel:
                weak_points.append({"knowledge_point_id": kp_opts[sel], "score": round(score, 2)})

        st.divider()
        st.subheader("🎯 目标（可选）")
        targets = st.multiselect("学习目标", list(kp_opts.keys()), max_selections=3)
        target_ids = [kp_opts[t] for t in targets] if targets else None

        max_n = st.slider("路径长度", 3, 20, 10)
        if st.button("🚀 生成学习路径", type="primary", use_container_width=True, key="gen_lp"):
            with st.spinner("Neo4j 图遍历 + LLM 建议..."):
                resp = api_post("/api/learning-path/generate", {
                    "user_id": "demo", "weak_points": weak_points,
                    "target_ids": target_ids, "max_nodes": max_n,
                })
            st.session_state.lp_result = resp
        else:
            if "lp_result" not in st.session_state:
                st.session_state.lp_result = api_post("/api/learning-path/generate", {
                    "user_id": "demo",
                    "weak_points": [{"knowledge_point_id": "kp_recursion", "score": 0.3}],
                    "target_ids": ["kp_dp"], "max_nodes": 5,
                })

    with c_out:
        resp = st.session_state.get("lp_result", {})
        if resp.get("nodes"):
            st.success(f"已生成 {len(resp['nodes'])} 步学习路径")

            # 路径图
            pn, pe, prev_n = [], [], None
            for node in resp["nodes"]:
                kp = node["knowledge_point"]
                c = kp_color(kp.get("category", ""))
                pn.append(Node(id=kp["id"], label=kp["name"], size=35, color=c))
                if prev_n:
                    pe.append(Edge(source=prev_n, target=kp["id"]))
                prev_n = kp["id"]
            agraph(nodes=pn, edges=pe, config=Config(
                width=750, height=250, directed=True, physics=False,
                hierarchical=True, direction="LR", nodeSpacing=120, levelSeparation=150,
            ))

            # 卡片
            for node in resp["nodes"]:
                kp = node["knowledge_point"]
                c = kp_color(kp.get("category", ""))
                with st.container(border=True):
                    cols = st.columns([0.08, 0.92])
                    with cols[0]:
                        st.markdown(f"## {node['order']}")
                    with cols[1]:
                        st.markdown(f"### :{c}[●] {kp['name']}")
                        st.caption(f"{kp.get('category','')} | {stars(kp.get('difficulty',1))}")
                        st.markdown(kp.get("description", ""))
                        st.info(f"💡 {node['reason']}")

            st.caption(f"生成时间: {resp.get('generated_at', '')}")
        elif "error" in resp:
            st.error(resp["error"])
        else:
            st.info("👈 选择薄弱知识点，点击生成学习路径")


# ==================== Footer ====================
st.divider()
st.caption("SmartLearn AI Platform · FastAPI + Streamlit · 2026")
