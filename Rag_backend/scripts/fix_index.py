from __future__ import annotations
import sys
from pathlib import Path

# 添加项目根目录到 path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db import Database

def fix():
    db = Database()
    session = db.neo4j.session()
    try:
        print("1. 正在尝试清理旧索引 (artifact_vector_index)...")
        session.run("DROP INDEX artifact_vector_index IF EXISTS").consume()
        
        print("2. 正在创建 1024 维度的全新 BGE-M3 向量索引...")
        # 直接使用包含反引号的原始 Cypher，不通过命令行传递，避免转义错误
        cypher = (
            "CREATE VECTOR INDEX artifact_vector_index IF NOT EXISTS "
            "FOR (n:Artifact) ON (n.embedding) "
            "OPTIONS {indexConfig: {`vector.dimensions`: 1024, `vector.similarity_function`: 'cosine'}}"
        )
        session.run(cypher).consume()
        
        print("3. 正在检查索引状态...")
        res = session.run("SHOW INDEXES YIELD name, state, type WHERE name = 'artifact_vector_index'").data()
        print(f"当前索引状态: {res}")
        
        if res and res[0]['state'] in ['ONLINE', 'POPULATING']:
            print("\n✅ 索引已重置！维度已对齐为 1024。")
            print("注意：如果状态是 POPULATING，说明 Neo4j 正在后台构建索引，请等待约 10 秒后提问即可。")
        else:
            print("\n❌ 索引创建可能未完全成功，请检查 Neo4j 是否正常运行。")
            
    finally:
        db.close()

if __name__ == "__main__":
    fix()
