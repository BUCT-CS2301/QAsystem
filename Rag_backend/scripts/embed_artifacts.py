from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings
from app.db import Database
from app.services.llm_client import LLMClient


def build_document(row: dict) -> str:
    title = clean(row.get("title")) or "未命名文物"
    parts = [f"文物《{title}》"]
    append(parts, "编号", row.get("accession_number") or row.get("object_id"))
    append(parts, "时期/朝代", row.get("periods"))
    append(parts, "核心材质", row.get("materials"))
    append(parts, "文物品类", row.get("types"))
    append(parts, "馆藏博物馆", row.get("museums"))
    append(parts, "尺寸", row.get("dimensions"))
    append(parts, "简介", row.get("description"))
    return "；".join(parts) + "。"


def append(parts: list[str], label: str, value) -> None:
    text = clean(value)
    if text:
        parts.append(f"{label}：{text}")


def clean(value) -> str:
    if isinstance(value, list):
        items = [clean(item) for item in value]
        return "、".join(dict.fromkeys(item for item in items if item and item != "unknown"))
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() in {"unknown", "none", "null", ""} else text


def fetch_artifacts(db: Database, limit: int | None, only_missing: bool) -> list[dict]:
    where = "WHERE a.embedding IS NULL OR a.text IS NULL" if only_missing else ""
    limit_clause = "LIMIT $limit" if limit else ""
    query = f"""
    MATCH (a:Artifact)
    {where}
    OPTIONAL MATCH (a)-[:所属朝代]->(p:Period)
    OPTIONAL MATCH (a)-[:制作材质]->(m:Material)
    OPTIONAL MATCH (a)-[:文物品类]->(t:ArtifactType)
    OPTIONAL MATCH (a)-[:收藏馆藏]->(museum:Museum)
    RETURN a.object_id AS object_id,
           a.title AS title,
           a.description AS description,
           a.dimensions AS dimensions,
           a.accession_number AS accession_number,
           collect(DISTINCT p.name) AS periods,
           collect(DISTINCT m.name) AS materials,
           collect(DISTINCT t.name) AS types,
           collect(DISTINCT coalesce(museum.name, museum.name_en)) AS museums
    ORDER BY a.object_id
    {limit_clause}
    """
    with db.neo4j.session() as session:
        return [dict(record) for record in session.run(query, limit=limit)]


def write_embeddings(db: Database, rows: list[dict], vectors: list[list[float]]) -> None:
    payload = []
    for row, vector in zip(rows, vectors):
        payload.append(
            {
                "object_id": row["object_id"],
                "text": row["text"],
                "embedding": vector,
            }
        )
    with db.neo4j.session() as session:
        session.run(
            """
            UNWIND $rows AS row
            MATCH (a:Artifact {object_id: row.object_id})
            SET a.text = row.text,
                a.embedding = row.embedding,
                a.embedding_model = $embedding_model,
                a.embedding_updated_at = datetime()
            """,
            rows=payload,
            embedding_model=settings.llm.embedding_model,
        ).consume()


def ensure_vector_index(db: Database, dimensions: int) -> None:
    with db.neo4j.session() as session:
        exists = session.run(
            "SHOW INDEXES YIELD name WHERE name = $name RETURN count(*) AS count",
            name=settings.rag.vector_index_name,
        ).single()["count"]
        if exists:
            return
        session.run(
            f"""
            CREATE VECTOR INDEX {settings.rag.vector_index_name} IF NOT EXISTS
            FOR (a:Artifact) ON (a.{settings.rag.vector_property})
            OPTIONS {{indexConfig: {{
                `vector.dimensions`: $dimensions,
                `vector.similarity_function`: 'cosine'
            }}}}
            """,
            dimensions=dimensions,
        ).consume()


def main() -> None:
    parser = argparse.ArgumentParser(description="把 Neo4j 文物图谱打平成文档并写入向量索引。")
    parser.add_argument("--limit", type=int, default=None, help="只处理前 N 条，便于测试。")
    parser.add_argument("--batch-size", type=int, default=32, help="Embedding API 批量大小。")
    parser.add_argument("--rebuild", action="store_true", help="重建所有文物向量；默认只补缺失。")
    args = parser.parse_args()

    db = Database()
    client = LLMClient()
    try:
        rows = fetch_artifacts(db, args.limit, only_missing=not args.rebuild)
        if not rows:
            print("没有需要处理的文物。")
            return

        total = len(rows)
        first_index_ready = False
        for start in range(0, total, args.batch_size):
            batch = rows[start : start + args.batch_size]
            for row in batch:
                row["text"] = build_document(row)

            vectors = client.embed_batch([row["text"] for row in batch])
            if not first_index_ready:
                ensure_vector_index(db, len(vectors[0]))
                first_index_ready = True

            write_embeddings(db, batch, vectors)
            print(f"已处理 {min(start + len(batch), total)}/{total}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
