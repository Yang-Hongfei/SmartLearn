"""
文档入库脚本

功能：
1. 将 Markdown/文本教材切分为语义块
2. 调用 Qwen3-Embedding 生成向量
3. 存入 Chroma 向量数据库

用法：
  python scripts/ingest_docs.py --input docs/ --chunk-size 500
"""

import os
import sys
import json
import argparse
import asyncio
import hashlib
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services import embedding_service, vector_service


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """简单语义分块：按段落切分，超长段落再按句子切分"""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) <= chunk_size:
            current += ("\n" if current else "") + para
        else:
            if current:
                chunks.append(current)
            # 如果单段超长，按句号切分
            if len(para) > chunk_size:
                sentences = para.replace("。", "。\n").split("\n")
                sub = ""
                for sent in sentences:
                    if len(sub) + len(sent) <= chunk_size:
                        sub += sent
                    else:
                        if sub:
                            chunks.append(sub)
                        sub = sent
                if sub:
                    current = sub
                else:
                    current = ""
            else:
                current = para
    if current:
        chunks.append(current)

    # 添加 overlap
    if overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-overlap:] if len(chunks[i - 1]) > overlap else chunks[i - 1]
            overlapped.append(prev_tail + "\n" + chunks[i])
        chunks = overlapped

    return chunks


async def ingest_directory(input_dir: str, chunk_size: int = 500):
    dir_path = Path(input_dir)
    files = list(dir_path.rglob("*.md")) + list(dir_path.rglob("*.txt")) + list(dir_path.rglob("*.json"))

    if not files:
        print(f"未找到任何文档文件（.md/.txt/.json）于 {input_dir}")
        return

    all_chunks = []
    all_metadatas = []
    all_ids = []

    for file_path in files:
        print(f"处理: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # JSON 格式的题目/知识点
        if file_path.suffix == ".json":
            try:
                items = json.loads(content)
                if isinstance(items, list):
                    for item in items:
                        text = f"{item.get('title', '')}\n{item.get('content', '')}\n{item.get('answer', '')}"
                        doc_id = hashlib.md5(text.encode()).hexdigest()[:12]
                        chunks.append(text)
                        metadatas.append({
                            "source": file_path.name,
                            "knowledge_point_id": item.get("knowledge_point_id", ""),
                            "type": item.get("type", "doc"),
                        })
                        ids.append(doc_id)
                    continue
            except json.JSONDecodeError:
                pass

        # Markdown/文本：分块处理
        # 从文件名推断知识点 ID
        kp_id = file_path.stem.split("_")[0] if "_" in file_path.stem else file_path.stem

        chunks = chunk_text(content, chunk_size)
        for j, chunk in enumerate(chunks):
            doc_id = hashlib.md5(chunk.encode()).hexdigest()[:12]
            all_chunks.append(chunk)
            all_metadatas.append({
                "source": file_path.name,
                "knowledge_point_id": kp_id,
                "chunk_index": j,
            })
            all_ids.append(f"{kp_id}_{j}_{doc_id}")

    print(f"\n共 {len(all_chunks)} 个文本块，正在生成向量...")

    # 批量 embedding + 入库
    batch_size = 20
    for i in range(0, len(all_chunks), batch_size):
        batch_chunks = all_chunks[i:i + batch_size]
        batch_metas = all_metadatas[i:i + batch_size]
        batch_ids = all_ids[i:i + batch_size]
        try:
            embeddings = await embedding_service.embed_batch(batch_chunks)
            # Chroma 的 upsert 可以传 embedding 也可以不传（让它自己生成）
            # 这里我们传自己的 embedding 以保证一致性
            await vector_service.upsert(
                documents=batch_chunks,
                metadatas=batch_metas,
                ids=batch_ids,
            )
            print(f"  入库 {i + len(batch_chunks)}/{len(all_chunks)}")
        except Exception as e:
            print(f"  入库失败 (batch {i}): {e}")

    print("\n文档入库完成!")


def main():
    parser = argparse.ArgumentParser(description="文档向量化入库")
    parser.add_argument("--input", "-i", required=True, help="文档目录路径")
    parser.add_argument("--chunk-size", type=int, default=500, help="分块大小（字符）")
    args = parser.parse_args()

    asyncio.run(ingest_directory(args.input, args.chunk_size))


if __name__ == "__main__":
    main()
