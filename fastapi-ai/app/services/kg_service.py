"""Neo4j 图数据库操作 —— 知识图谱存储、查询、路径规划。

核心概念：
- KnowledgePoint 节点：代表一个算法知识点（名称、描述、难度、分类）
- PREREQUISITE 关系：A 是 B 的前置知识（学 B 前必须先学 A）
- RELATED_TO 关系：A 与 B 相关但不强制先后顺序

Cypher 查询说明：
- 变量路径 `-[*1..n]-` 的跳数必须是字面量，不能参数化
  所以 find_shortest_path 用 f-string 拼接 max_depth，需确保是 int
"""

from neo4j import GraphDatabase
from app.core.config import settings

# 模块级 Driver 单例：连接池自动管理，复用 TCP 连接
_driver = None


def get_driver() -> GraphDatabase.driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


def close_driver():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


# ==================== 知识点 CRUD ====================

async def create_knowledge_point(kp: dict) -> dict:
    """创建或更新知识点（MERGE：id 存在则更新属性）"""
    driver = get_driver()
    with driver.session() as session:
        result = session.run(
            """
            MERGE (k:KnowledgePoint {id: $id})
            SET k.name = $name, k.description = $description,
                k.difficulty = $difficulty, k.category = $category
            RETURN k {.id, .name, .description, .difficulty, .category} AS kp
            """,
            **kp,
        )
        record = result.single()
        return dict(record["kp"]) if record else {}


async def get_knowledge_point(kp_id: str) -> dict | None:
    """按 ID 查单个知识点"""
    driver = get_driver()
    with driver.session() as session:
        result = session.run(
            "MATCH (k:KnowledgePoint {id: $id}) "
            "RETURN k {.id, .name, .description, .difficulty, .category} AS kp",
            id=kp_id,
        )
        record = result.single()
        return dict(record["kp"]) if record else None


async def search_knowledge_points(
    keyword: str, category: str | None = None, limit: int = 10
) -> list[dict]:
    """按名称或描述搜索知识点，支持按分类过滤"""
    driver = get_driver()
    category_filter = "AND k.category = $category" if category else ""
    with driver.session() as session:
        result = session.run(
            f"""
            MATCH (k:KnowledgePoint)
            WHERE (k.name CONTAINS $keyword OR k.description CONTAINS $keyword)
            {category_filter}
            RETURN k {{.id, .name, .description, .difficulty, .category}} AS kp
            LIMIT $limit
            """,
            keyword=keyword, category=category, limit=limit,
        )
        return [dict(record["kp"]) for record in result]


# ==================== 关系操作 ====================

async def create_relation(
    from_id: str, to_id: str, rel_type: str = "PREREQUISITE", weight: float = 1.0
) -> bool:
    """创建两个知识点之间的关系（MERGE：已存在则更新权重）"""
    driver = get_driver()
    type_upper = rel_type.upper()  # 关系类型大写（如 PREREQUISITE）
    with driver.session() as session:
        result = session.run(
            f"""
            MATCH (a:KnowledgePoint {{id: $from_id}})
            MATCH (b:KnowledgePoint {{id: $to_id}})
            MERGE (a)-[r:{type_upper}]->(b)
            SET r.weight = $weight
            RETURN r
            """,
            from_id=from_id, to_id=to_id, weight=weight,
        )
        return result.single() is not None


async def get_related_points(kp_id: str) -> list[dict]:
    """获取与某知识点直接相邻的所有节点（不限方向、不限关系类型）"""
    driver = get_driver()
    with driver.session() as session:
        result = session.run(
            """
            MATCH (k:KnowledgePoint {id: $id})-[r]-(related:KnowledgePoint)
            RETURN related {.id, .name, .description, .difficulty, .category} AS kp,
                   type(r) AS relation, r.weight AS weight
            LIMIT 50
            """,
            id=kp_id,
        )
        return [
            {**dict(record["kp"]), "relation": record["relation"], "weight": record["weight"]}
            for record in result
        ]


async def get_prerequisites(kp_id: str) -> list[dict]:
    """获取某知识点的所有前置依赖（沿 PREREQUISITE 关系向前追溯）"""
    driver = get_driver()
    with driver.session() as session:
        result = session.run(
            """
            MATCH (k:KnowledgePoint {id: $id})-[r:PREREQUISITE*1..]->(prereq:KnowledgePoint)
            RETURN prereq {.id, .name, .description, .difficulty, .category} AS kp
            """,
            id=kp_id,
        )
        return [dict(record["kp"]) for record in result]


# ==================== 图路径查询 ====================

async def find_shortest_path(
    from_id: str, to_id: str, max_depth: int = 5
) -> list[dict] | None:
    """两个知识点之间的最短路径（Neo4j 内置 shortestPath 算法）。

    注意：`[*1..{max_depth}]` 必须用 f-string 拼接，
    因为 Cypher 不支持参数化的变长路径跳数。
    """
    driver = get_driver()
    with driver.session() as session:
        result = session.run(
            f"""
            MATCH path = shortestPath(
                (start:KnowledgePoint {{id: $from_id}})-[*1..{int(max_depth)}]-(end:KnowledgePoint {{id: $to_id}})
            )
            RETURN [node in nodes(path) | node {{.id, .name, .description, .difficulty, .category}}] AS nodes,
                   length(path) AS length
            ORDER BY length
            LIMIT 1
            """,
            from_id=from_id, to_id=to_id,
        )
        record = result.single()
        if record:
            return [dict(node) for node in record["nodes"]]
        return None


async def get_all_categories() -> list[str]:
    """获取所有知识点的分类列表（用于前端筛选器）"""
    driver = get_driver()
    with driver.session() as session:
        result = session.run(
            "MATCH (k:KnowledgePoint) RETURN DISTINCT k.category AS category ORDER BY category"
        )
        return [record["category"] for record in result if record["category"]]
