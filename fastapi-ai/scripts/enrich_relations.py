"""
用 LLM 为孤立知识节点推断 PREREQUISITE / RELATED_TO 关系。

用法：python scripts/enrich_relations.py
"""
import json
import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.services import llm_service, kg_service
from neo4j import GraphDatabase
from app.core.config import settings

RELATION_PROMPT = """你是一个知识图谱专家。下面是同一分类下的知识点列表。请为它们推断学习依赖关系。

每个知识点格式：{id: "kp_xxx", name: "名称", description: "描述"}

请分析这些知识点之间的 PREREQUISITE（必须前置学习）和 RELATED_TO（相互关联）关系。

输出 JSON 数组：
[
  {"from": "kp_A", "to": "kp_B", "type": "PREREQUISITE", "weight": 0.8, "reason": "学B前必须先掌握A"},
  {"from": "kp_C", "to": "kp_D", "type": "RELATED_TO", "weight": 0.6, "reason": "两者概念相近"}
]

规则：
- PREREQUISITE: A 是 B 的前置基础（基础概念 → 进阶概念）
- RELATED_TO: 两知识点有交叉或互补
- weight: 0.0-1.0，表示关系强度，基础概念 → 进阶概念 ≥0.7，同级关联0.3-0.6
- 不要编造不存在的知识点ID
- 只输出 JSON 数组，不要其他内容"""


async def main():
    driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))

    # Step 1: 收集有关系的节点，找出孤立节点
    with driver.session() as session:
        orphan_result = session.run("""
            MATCH (k:KnowledgePoint)
            WHERE NOT (k)-[:PREREQUISITE|RELATED_TO]-()
            RETURN k.id AS id, k.name AS name, k.description AS desc, k.category AS cat
            ORDER BY k.category, k.name
        """)
        orphans = [dict(r) for r in orphan_result]

    if not orphans:
        print("没有孤立节点，所有节点都已有关系！")
        driver.close()
        return

    print(f"找到 {len(orphans)} 个孤立节点")

    # 按分类分组
    groups = {}
    for node in orphans:
        cat = node["cat"]
        if cat not in groups:
            groups[cat] = []
        groups[cat].append(node)

    print(f"共 {len(groups)} 个分类")

    # Step 2: 逐分类用 LLM 推断关系
    total_relations = 0
    for cat, nodes in sorted(groups.items()):
        # 每批最多 30 个节点
        for batch_start in range(0, len(nodes), 30):
            batch = nodes[batch_start:batch_start + 30]
            if len(batch) < 2:
                continue

            # 构建 LLM 输入
            node_list = [{"id": n["id"], "name": n["name"], "description": n["desc"]} for n in batch]
            node_text = json.dumps(node_list, ensure_ascii=False, indent=2)

            print(f"  分析「{cat}」({batch_start + 1}-{batch_start + len(batch)}/{len(nodes)} 个节点)...", end=" ")

            try:
                response = await llm_service.chat([
                    {"role": "system", "content": RELATION_PROMPT},
                    {"role": "user", "content": node_text},
                ])

                # 解析 JSON
                start = response.find("[")
                end = response.rfind("]") + 1
                if start >= 0 and end > start:
                    rels = json.loads(response[start:end])

                    # 验证并导入
                    valid_ids = {n["id"] for n in batch}
                    imported = 0
                    for rel in rels:
                        if rel.get("from") in valid_ids and rel.get("to") in valid_ids:
                            rel_type = rel.get("type", "RELATED_TO")
                            if rel_type not in ("PREREQUISITE", "RELATED_TO"):
                                rel_type = "RELATED_TO"
                            try:
                                await kg_service.create_relation(
                                    from_id=rel["from"], to_id=rel["to"],
                                    rel_type=rel_type,
                                    weight=rel.get("weight", 0.5),
                                )
                                imported += 1
                            except Exception as e:
                                pass
                    print(f"→ {imported} 条关系")
                    total_relations += imported
                else:
                    print("→ 解析失败")
            except Exception as e:
                print(f"→ 错误: {e}")

    # Step 3: 为依然孤立的节点建立 RELATED_TO 关系（同分类内兜底）
    print(f"\n兜底：同分类孤立节点互连...")
    with driver.session() as session:
        still_orphans = session.run("""
            MATCH (k:KnowledgePoint)
            WHERE NOT (k)-[:PREREQUISITE|RELATED_TO]-()
            RETURN k.id AS id, k.name AS name, k.category AS cat
            ORDER BY k.category, k.name
        """)
        still = [dict(r) for r in still_orphans]

    pending_groups = {}
    for n in still:
        cat = n["cat"]
        if cat not in pending_groups:
            pending_groups[cat] = []
        pending_groups[cat].append(n)

    fallback_created = 0
    for cat, nodes in pending_groups.items():
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                try:
                    await kg_service.create_relation(
                        from_id=nodes[i]["id"], to_id=nodes[j]["id"],
                        rel_type="RELATED_TO", weight=0.3,
                    )
                    fallback_created += 1
                except:
                    pass

    print(f"兜底创建 {fallback_created} 条关系")

    # Step 4: 最终统计
    with driver.session() as session:
        total_nodes = session.run("MATCH (k:KnowledgePoint) RETURN count(k) AS c").single()["c"]
        total_rels = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        orphans_left = session.run(
            "MATCH (k:KnowledgePoint) WHERE NOT (k)-[]-() RETURN count(k) AS c"
        ).single()["c"]

    print(f"\n========================================")
    print(f"总节点: {total_nodes}")
    print(f"总关系: {total_rels}")
    print(f"剩余孤立: {orphans_left}")
    print(f"本次新增: {total_relations + fallback_created} 条关系")
    driver.close()


if __name__ == "__main__":
    asyncio.run(main())
