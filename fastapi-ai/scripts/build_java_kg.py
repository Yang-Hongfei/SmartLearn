"""
从 questions 表提取所有知识点，构建 Java/Spring/MySQL 知识图谱。

用法：python scripts/build_java_kg.py
"""
import json
import re
import sys
import os
import asyncio
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.services import kg_service, llm_service

# ==================== 根据 KP ID 前缀 + topic 推断分类 ====================

CATEGORY_PATTERNS = {
    "spring": "Spring框架",
    "aop": "Spring AOP",
    "ioc": "Spring IoC",
    "spring_boot": "Spring Boot",
    "springboot": "Spring Boot",
    "spring_mvc": "Spring MVC",
    "springmvc": "Spring MVC",
    "spring_cloud": "Spring Cloud",
    "springcloud": "Spring Cloud",
    "mysql": "MySQL数据库",
    "innodb": "InnoDB存储引擎",
    "sql": "SQL语言",
    "database": "数据库设计",
    "data_type": "数据类型",
    "jvm": "JVM虚拟机",
    "gc": "JVM垃圾回收",
    "redis": "Redis缓存",
    "distributed": "分布式系统",
    "lock": "分布式锁",
    "transaction": "事务管理",
    "thread": "并发编程",
    "design_pattern": "设计模式",
    "reflection": "Java反射",
    "annotation": "Java注解",
    "proxy": "代理模式",
    "container": "容器",
    "bean": "Spring Bean",
    "cache": "缓存",
    "mvc": "Spring MVC",
    "web": "Web开发",
    "oop": "面向对象",
    "class": "类加载",
    "jdk": "JDK",
    "cglib": "CGlib代理",
    "aspectj": "AspectJ",
    "log": "日志",
    "character": "字符集",
    "storage": "存储引擎",
    "memory": "内存管理",
    "buffer": "缓冲池",
    "index": "索引",
    "hash": "哈希",
    "binary": "二叉树/查找",
    "sort": "排序算法",
    "search": "搜索算法",
    "graph": "图论",
    "dp": "动态规划",
    "greedy": "贪心算法",
    "linked_list": "链表",
    "array": "数组",
    "stack": "栈",
    "queue": "队列",
    "tree": "树",
    "backtracking": "回溯算法",
    "sliding_window": "滑动窗口",
    "two_pointers": "双指针",
    "prefix_sum": "前缀和",
    "recursion": "递归",
    "divide_conquer": "分治法",
    "time_complexity": "复杂度分析",
    "space_complexity": "复杂度分析",
    "knapsack": "背包问题",
    "lcs": "动态规划",
    "lis": "动态规划",
    "memoization": "动态规划",
    "bfs": "图搜索",
    "dfs": "图搜索",
    "dijkstra": "图论",
    "topological": "图论",
    "count": "SQL函数",
    "union": "SQL查询",
    "limit": "SQL查询",
    "function": "SQL函数",
    "command": "SQL命令",
    "join": "SQL查询",
    "normalization": "数据库设计",
    "table_design": "数据库设计",
    "null": "SQL陷阱",
    "execution": "SQL执行",
    "parse": "SQL解析",
    "architecture": "MySQL架构",
    "segment": "InnoDB结构",
    "page": "InnoDB页结构",
    "pool": "缓冲池",
    "lru": "缓存算法",
    "binlog": "MySQL日志",
    "redo": "MySQL日志",
    "undo": "MySQL日志",
    "wal": "MySQL机制",
}


def infer_category(kp_id: str, topic: str = "") -> str:
    """根据 ID 前缀字符串匹配推断分类"""
    kp_lower = kp_id.lower()
    for pattern, cat in CATEGORY_PATTERNS.items():
        if pattern in kp_lower:
            return cat
    return "其他"


def infer_name(kp_id: str) -> str:
    """从 kp_id 推断可读名称（去掉前缀、分隔符转空格）"""
    # 去掉常见前缀
    name = kp_id
    for prefix in ["kp_", "spring_", "mysql_", "innodb_", "database_", "jvm_"]:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    name = name.replace("_", " ").strip()
    # 首字母大写
    return " ".join(w.capitalize() if w.islower() else w for w in name.split())


# ==================== 关系推导规则 ====================

# 定义知识领域内层级：基础 → 进阶 → 高级
DOMAIN_HIERARCHY = {
    "Spring框架": {
        "layers": [
            ["spring_intro", "spring_features", "spring_modules", "spring_annotations"],
            ["ioc", "di", "ioc_container", "bean_registration", "dependency_injection",
             "spring_ioc", "spring_ioc_mechanism", "spring_ioc_understanding"],
            ["beanfactory", "applicationcontext", "spring_container"],
            ["spring_bean", "spring_bean_lifecycle", "spring_bean_scope",
             "spring_aware_interface", "spring_init_destroy_method",
             "spring_autowired", "spring_resource", "spring_autowiring",
             "component_bean_difference", "component_scan"],
            ["spring_circular_dependency", "spring_cycle_dependency", "spring_three_level_cache"],
        ]
    },
    "Spring AOP": {
        "layers": [
            ["aop", "aop_oop_relationship", "aop_application_scenarios"],
            ["spring_aop_concepts", "spring_aop_weaving", "spring_aop_advice",
             "spring_aop_timing", "spring_aop_summary"],
            ["aspectj", "spring_aop", "jdk_dynamic_proxy", "cglib_proxy"],
        ]
    },
    "Spring Boot": {
        "layers": [
            ["spring_boot_intro", "spring_boot_auto_configuration", "spring_boot_starter"],
            ["spring_boot_startup", "springtask", "spring_cache"],
        ]
    },
    "Spring MVC": {
        "layers": [
            ["spring_mvc_components", "spring_mvc_workflow", "spring_mvc_restful"],
        ]
    },
    "Spring事务": {
        "layers": [
            ["spring_transaction", "transaction_isolation", "transaction_propagation",
             "transaction_failure"],
        ]
    },
    "MySQL数据库": {
        "layers": [
            ["mysql_basics", "mysql_architecture", "sql_execution_process"],
            ["mysql_performance", "storage_engine_selection", "innodb_myisam_difference"],
            ["mysql_join", "mysql_commands", "mysql_functions", "mysql_limit"],
            ["innodb_memory_structure", "innodb_buffer_pool", "innodb_data_page_structure"],
            ["mysql_binlog", "mysql_redo_log", "mysql_undo_log", "mysql_wal"],
            ["sql_execution_order", "sql_parse_tree", "sql_implicit_conversion"],
        ]
    },
    "数据库设计": {
        "layers": [
            ["database_normalization", "table_design"],
            ["data_type_varchar_char", "data_type_blob_text", "data_type_datetime_timestamp",
             "data_type_currency", "data_type_float_double"],
            ["null_value_trap", "character_set_emoji"],
        ]
    },
}

# 跨域关系（MySQL → Spring 集成点等）
CROSS_DOMAIN_RELATIONS = [
    ("spring_cache", "redis", "PREREQUISITE", 0.5, "Spring缓存集成依赖Redis"),
    ("spring_transaction", "mysql_performance", "RELATED_TO", 0.5, "事务管理影响数据库性能"),
    ("jdbc", "mysql_basics", "PREREQUISITE", 0.7, "JDBC是Java连接MySQL的基础"),
    ("jdbc_template", "jdbc", "PREREQUISITE", 0.8, "JdbcTemplate封装了JDBC"),
    ("mybatis", "jdbc", "PREREQUISITE", 0.6, "MyBatis底层基于JDBC"),
]


def build_relations(all_kp_ids: set[str], topic_map: dict) -> list[dict]:
    """基于层级规则 + 跨域规则生成关系列表"""
    relations = []
    all_lower = {k.lower(): k for k in all_kp_ids}

    # 1. 域内层级关系
    for domain, config in DOMAIN_HIERARCHY.items():
        layers = config.get("layers", [])
        # 同层 RELATED_TO
        for layer in layers:
            layer_ids = []
            for pid in layer:
                matched = None
                for aid, real_id in all_lower.items():
                    if aid == pid or aid.endswith(pid):
                        matched = real_id
                        break
                if matched:
                    layer_ids.append(matched)
            for i in range(len(layer_ids)):
                for j in range(i + 1, len(layer_ids)):
                    relations.append({
                        "from": layer_ids[i], "to": layer_ids[j],
                        "type": "RELATED_TO", "weight": 0.5,
                    })
        # 层间 PREREQUISITE（下层是上层的前置）
        for l in range(len(layers) - 1):
            lower_layer = []
            upper_layer = []
            for pid in layers[l]:
                for aid, real_id in all_lower.items():
                    if aid == pid or aid.endswith(pid):
                        lower_layer.append(real_id)
                        break
            for pid in layers[l + 1]:
                for aid, real_id in all_lower.items():
                    if aid == pid or aid.endswith(pid):
                        upper_layer.append(real_id)
                        break
            for low in lower_layer:
                for up in upper_layer:
                    relations.append({
                        "from": low, "to": up,
                        "type": "PREREQUISITE", "weight": 0.7,
                    })

    # 2. 跨域关系
    for a, b, rtype, w, _ in CROSS_DOMAIN_RELATIONS:
        a_real = all_lower.get(a, a)
        b_real = all_lower.get(b, b)
        if a_real in all_kp_ids and b_real in all_kp_ids:
            relations.append({"from": a_real, "to": b_real, "type": rtype, "weight": w})

    # 3. 去重
    seen_pairs = set()
    unique_relations = []
    for r in relations:
        pair = (r["from"], r["to"], r["type"])
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            unique_relations.append(r)

    return unique_relations


async def main():
    # Step 1: 从数据库提取所有唯一 KP ID
    print("Step 1: 从数据库提取知识点...")
    import mysql.connector
    conn = mysql.connector.connect(
        host="localhost", port=3306, user="root", password="666666",
        database="smartlearn", charset="utf8mb4",
    )
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT knowledge_point_ids, topic FROM questions "
        "WHERE knowledge_point_ids IS NOT NULL AND knowledge_point_ids != '' AND knowledge_point_ids != '[]'"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # 解析所有唯一 KP ID
    all_kp_ids = set()
    topic_map = {}
    for kp_json, topic in rows:
        try:
            ids = json.loads(kp_json)
            for kp_id in ids:
                all_kp_ids.add(kp_id)
                if kp_id not in topic_map:
                    topic_map[kp_id] = topic
                elif topic and topic != topic_map[kp_id]:
                    topic_map[kp_id] = topic_map[kp_id] + "; " + topic
        except (json.JSONDecodeError, TypeError):
            pass

    print(f"  提取到 {len(all_kp_ids)} 个唯一知识点")

    # Step 2: 构建节点列表
    print("\nStep 2: 构建节点...")
    nodes = []
    for kp_id in sorted(all_kp_ids):
        topic = topic_map.get(kp_id, "")
        category = infer_category(kp_id, topic)
        name = infer_name(kp_id)
        nodes.append({
            "id": kp_id,
            "name": name,
            "description": f"{name}（分类：{category}）",
            "difficulty": 2,
            "category": category,
        })

    print(f"  生成 {len(nodes)} 个节点，分类分布：")
    cat_counts = {}
    for n in nodes:
        c = n["category"]
        cat_counts[c] = cat_counts.get(c, 0) + 1
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {cnt}")

    # Step 3: 构建关系
    print("\nStep 3: 生成关系...")
    relations = build_relations(all_kp_ids, topic_map)
    print(f"  生成 {len(relations)} 条关系")

    # Step 4: 保存为 JSON
    output = {"nodes": nodes, "relations": relations}
    output_path = os.path.join(os.path.dirname(__file__), "java_knowledge_graph.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nStep 4: 已保存到 {output_path}")

    # Step 5: 导入 Neo4j
    print("\nStep 5: 导入 Neo4j...")
    for i, node in enumerate(nodes):
        try:
            await kg_service.create_knowledge_point(node)
        except Exception as e:
            pass  # MERGE 幂等，已有就跳过

    for i, rel in enumerate(relations):
        try:
            await kg_service.create_relation(
                from_id=rel["from"], to_id=rel["to"],
                rel_type=rel["type"], weight=rel["weight"],
            )
        except Exception as e:
            pass

    print(f"\n导入完成: {len(nodes)} 个节点, {len(relations)} 条关系")
    print(f"JSON 文件: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
