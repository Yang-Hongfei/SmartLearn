"""
知识图谱构建脚本

功能：
1. 从教材知识点列表构建 Neo4j 知识图谱
2. 支持批量导入知识点节点和关系
3. 可选：调用 LLM 从原始文本抽取知识点

用法：
  python scripts/build_kg.py --input knowledge_points.json
  python scripts/build_kg.py --extract --source docs/algorithms.txt
"""

import json
import argparse
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.services import kg_service, llm_service

EXTRACT_PROMPT = """从以下算法教材文本中提取所有知识点。

对每个知识点输出 JSON：
{
  "id": "唯一英文ID（如 kp_recursion）",
  "name": "中文名称",
  "description": "一句话定义",
  "difficulty": 1-5,
  "category": "分类（如：算法思想 / 数据结构 / 排序 / 搜索 / 图论 / 动态规划）"
}

只输出 JSON 数组，不要其他内容。"""


async def build_from_json(input_file: str):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    relations = data.get("relations", [])

    print(f"导入 {len(nodes)} 个知识点...")
    for node in nodes:
        await kg_service.create_knowledge_point(node)
        print(f"  [节点] {node['id']}: {node['name']}")

    print(f"\n导入 {len(relations)} 条关系...")
    for rel in relations:
        ok = await kg_service.create_relation(
            from_id=rel["from"],
            to_id=rel["to"],
            rel_type=rel.get("type", "PREREQUISITE"),
            weight=rel.get("weight", 1.0),
        )
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {rel['from']} -[{rel.get('type', 'PREREQUISITE')}]-> {rel['to']}")

    print("\n知识图谱构建完成!")
async def extract_from_text(source_file: str):
    with open(source_file, "r", encoding="utf-8") as f:
        text = f.read()

    # 分块（每块约 3000 字）
    chunk_size = 3000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    all_kps = []
    for i, chunk in enumerate(chunks):
        print(f"抽取第 {i + 1}/{len(chunks)} 块...")
        response = await llm_service.chat([
            {"role": "system", "content": EXTRACT_PROMPT},
            {"role": "user", "content": chunk},
        ])
        # 提取 JSON
        try:
            start = response.index("[")
            end = response.rindex("]") + 1
            kps = json.loads(response[start:end])
            all_kps.extend(kps)
            print(f"  抽取到 {len(kps)} 个知识点")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"  解析失败: {e}")

    # 去重（按 name）
    seen_names = set()
    unique = []
    for kp in all_kps:
        if kp["name"] not in seen_names:
            seen_names.add(kp["name"])
            unique.append(kp)

    # 保存结果
    output_file = source_file.replace(".txt", "_kg.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"nodes": unique, "relations": []}, f, ensure_ascii=False, indent=2)

    print(f"\n抽取完成，共 {len(unique)} 个知识点，已保存到 {output_file}")
    print("关系（relations）需手动标注，或通过后续脚本补充。")

def main():
    parser = argparse.ArgumentParser(description="构建知识图谱")
    parser.add_argument("--input", "-i", help="知识点 JSON 文件路径")
    parser.add_argument("--extract", action="store_true", help="从文本抽取知识点")
    parser.add_argument("--source", "-s", help="源文本文件路径")
    args = parser.parse_args()

    if args.extract and args.source:
        asyncio.run(extract_from_text(args.source))
    elif args.input:
        asyncio.run(build_from_json(args.input))
    else:
        parser.print_help()
if __name__ == "__main__":
    main()
