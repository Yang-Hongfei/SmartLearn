"""学习路径规划 —— 根据薄弱点 + 知识图谱生成最优学习顺序。

算法逻辑：
1. 薄弱点按掌握度升序排列（最弱的先学）
2. 从每个薄弱点出发，沿 PREREQUISITE 关系向上追溯前置知识
3. 如果指定了目标，用 Neo4j shortestPath 找从薄弱点到目标的路径
4. 所有节点合并去重，确保前置知识点排在前面（拓扑序）
5. LLM 为每个节点生成一句话学习建议
"""

from app.services import kg_service, llm_service

PATH_SYSTEM_PROMPT = """你是一个算法学习路径规划助手。根据知识图谱分析结果，生成简短的学习路径建议。

每个节点给出：
1. 先学什么（前置知识点）
2. 核心概念一句话说明
3. 常见错误/注意事项
用中文回答，保持每条建议在 150 字以内。"""


async def generate_learning_path(
    user_id: str,
    weak_points: list[tuple[str, float]],  # [(kp_id, mastery_score), ...]
    target_ids: list[str] | None = None,
    max_nodes: int = 10,
) -> list[dict]:
    """生成个性化学习路径。返回排序后的节点列表，每个节点含 LLM 建议。

    weak_points: (知识点ID, 掌握度) 元组列表，0.0=完全不会，1.0=已掌握
    """
    # 最弱的先处理
    sorted_weak = sorted(weak_points, key=lambda x: x[1])

    path_nodes: list[dict] = []
    seen_kp_ids: set[str] = set()

    # 阶段 1：收集薄弱点 + 其前置依赖
    for kp_id, score in sorted_weak:
        if len(path_nodes) >= max_nodes:
            break

        # 薄弱点本身
        kp = await kg_service.get_knowledge_point(kp_id)
        if kp and kp["id"] not in seen_kp_ids:
            seen_kp_ids.add(kp["id"])
            path_nodes.append({**kp, "trigger": f"薄弱点（掌握度 {score:.0%}）"})

        # 向上追溯前置依赖（必须先补的基础知识）
        prereqs = await kg_service.get_prerequisites(kp_id)
        for prereq in prereqs[:2]:  # 最多取 2 个直接前置
            if len(path_nodes) >= max_nodes:
                break
            if prereq["id"] not in seen_kp_ids:
                seen_kp_ids.add(prereq["id"])
                path_nodes.append({**prereq, "trigger": f"为学好「{kp['name']}」需要先掌握的前置知识"})

    # 阶段 2：如果指定了目标，找最短路径
    if target_ids and len(path_nodes) < max_nodes:
        for kp_id, _ in sorted_weak:
            for target_id in target_ids:
                if len(path_nodes) >= max_nodes:
                    break
                intermediates = await kg_service.find_shortest_path(kp_id, target_id, max_depth=5)
                if intermediates:
                    for node in intermediates:
                        if node["id"] not in seen_kp_ids and len(path_nodes) < max_nodes:
                            seen_kp_ids.add(node["id"])
                            path_nodes.append({**node, "trigger": f"通往目标的路径节点"})

    # 阶段 3：LLM 为每个节点生成学习建议
    if path_nodes:
        node_names = " → ".join(n["name"] for n in path_nodes)
        prompt = (
            f"学习路径：{node_names}\n"
            f"请为路径中每个知识点用一句话给出学习建议，格式：知识点名：建议内容"
        )
        suggestions = await llm_service.chat_simple(prompt, system=PATH_SYSTEM_PROMPT)
    else:
        suggestions = ""

    # 按行解析 LLM 建议
    suggestions_map: dict[str, str] = {}
    for line in suggestions.split("\n"):
        if "：" in line or ":" in line:
            sep = "：" if "：" in line else ":"
            name, _, suggestion = line.partition(sep)
            suggestions_map[name.strip()] = suggestion.strip()

    # 组装最终结果
    result = []
    for i, node in enumerate(path_nodes):
        result.append({
            "order": i + 1,
            "knowledge_point": {
                "id": node["id"],
                "name": node["name"],
                "description": node.get("description", ""),
                "difficulty": node.get("difficulty", 1),
                "category": node.get("category", ""),
            },
            "reason": suggestions_map.get(node["name"], node.get("trigger", "")),
        })

    return result
