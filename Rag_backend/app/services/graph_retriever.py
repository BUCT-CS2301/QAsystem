from collections import defaultdict

from neo4j import Driver

from app.config import settings
from app.models import Artifact


LABEL_TO_FIELD = {
    "Period": "period",
    "Material": "material",
    "ArtifactType": "artifact_type",
    "Museum": "museum",
    "Image": "image_url",
}


class GraphRetriever:
    def __init__(self, driver: Driver) -> None:
        self.driver = driver

    def search_artifacts(self, keywords: list[str], limit: int | None = None) -> list[Artifact]:
        limit = limit or settings.result_limit
        if not keywords:
            return []
        artifacts: dict[str, Artifact] = {}
        with self.driver.session() as session:
            for keyword in keywords:
                records = session.run(
                    """
                    MATCH (a:Artifact)
                    WHERE toLower(coalesce(a.title, '')) CONTAINS toLower($keyword)
                       OR toLower(coalesce(a.description, '')) CONTAINS toLower($keyword)
                       OR toLower(coalesce(a.accession_number, '')) CONTAINS toLower($keyword)
                    RETURN a.object_id AS object_id,
                           a.title AS title,
                           a.description AS description,
                           a.dimensions AS dimensions,
                           a.accession_number AS accession_number
                    LIMIT $limit
                    """,
                    keyword=keyword,
                    limit=limit,
                )
                for record in records:
                    object_id = record["object_id"]
                    if not object_id:
                        continue
                    score = 2.0 if keyword in (record["title"] or "") else 1.0
                    existing = artifacts.get(object_id)
                    if existing:
                        existing.score += score
                    else:
                        artifacts[object_id] = Artifact(
                            object_id=object_id,
                            title=record["title"] or "",
                            description=record["description"] or "",
                            dimensions=record["dimensions"] or "",
                            accession_number=record["accession_number"] or "",
                            score=score,
                        )

        return sorted(artifacts.values(), key=lambda item: item.score, reverse=True)[:limit]

    def vector_search(self, query_vector: list[float], limit: int | None = None) -> list[Artifact]:
        limit = limit or settings.rag.result_limit
        # 多查一些以补偿去重后的损失
        fetch_limit = limit * 3
        with self.driver.session() as session:
            records = session.run(
                """
                CALL db.index.vector.queryNodes($index_name, $limit, $query_vector)
                YIELD node, score
                WHERE node:Artifact
                RETURN node.object_id AS object_id,
                       node.title AS title,
                       node.description AS description,
                       node.dimensions AS dimensions,
                       node.accession_number AS accession_number,
                       node.text AS text,
                       score
                ORDER BY score DESC
                """,
                index_name=settings.rag.vector_index_name,
                limit=fetch_limit,
                query_vector=query_vector,
            )
            artifacts = []
            seen_ids: set[str] = set()
            for record in records:
                object_id = record["object_id"] or ""
                # 按 object_id 去重，只保留得分最高的第一条
                if object_id in seen_ids:
                    continue
                seen_ids.add(object_id)
                artifact = Artifact(
                    object_id=object_id,
                    title=record["title"] or "",
                    description=record["text"] or record["description"] or "",
                    dimensions=record["dimensions"] or "",
                    accession_number=record["accession_number"] or "",
                    score=float(record["score"] or 0),
                )
                artifacts.append(artifact)
                if len(artifacts) >= limit:
                    break
            return artifacts

    def get_artifact_context(self, object_id: str) -> Artifact | None:
        with self.driver.session() as session:
            record = session.run(
                """
                MATCH (a:Artifact {object_id: $object_id})
                OPTIONAL MATCH (a)--(n)
                RETURN a.object_id AS object_id,
                       a.title AS title,
                       a.description AS description,
                       a.dimensions AS dimensions,
                       a.accession_number AS accession_number,
                       collect(DISTINCT {
                           labels: labels(n),
                           name: coalesce(n.name, n.value, n.url, '')
                       }) AS neighbors
                LIMIT 1
                """,
                object_id=object_id,
            ).single()

        if not record:
            return None

        artifact = Artifact(
            object_id=record["object_id"] or "",
            title=record["title"] or "",
            description=record["description"] or "",
            dimensions=record["dimensions"] or "",
            accession_number=record["accession_number"] or "",
        )
        self._apply_neighbors(artifact, record["neighbors"] or [])
        return artifact

    def search_by_facets(self, question: str, keywords: list[str], limit: int | None = None) -> list[Artifact]:
        limit = limit or settings.result_limit
        candidates: dict[str, Artifact] = {}
        search_terms = [question] + keywords

        with self.driver.session() as session:
            for term in search_terms:
                if not term:
                    continue
                records = session.run(
                    """
                    MATCH (a:Artifact)--(n)
                    WHERE any(label IN labels(n) WHERE label IN ['Period', 'Material', 'ArtifactType', 'Museum', 'Location'])
                      AND (
                          toLower(coalesce(n.name, '')) CONTAINS toLower($term)
                          OR toLower($term) CONTAINS toLower(coalesce(n.name, ''))
                      )
                    WITH DISTINCT a
                    OPTIONAL MATCH (a)--(ctx)
                    RETURN a.object_id AS object_id,
                           a.title AS title,
                           a.description AS description,
                           a.dimensions AS dimensions,
                           a.accession_number AS accession_number,
                           collect(DISTINCT {
                               labels: labels(ctx),
                               name: coalesce(ctx.name, ctx.value, ctx.url, '')
                           }) AS neighbors
                    LIMIT $limit
                    """,
                    term=term,
                    limit=limit,
                )
                for record in records:
                    object_id = record["object_id"]
                    if not object_id:
                        continue
                    artifact = candidates.get(object_id) or Artifact(
                        object_id=object_id,
                        title=record["title"] or "",
                        description=record["description"] or "",
                        dimensions=record["dimensions"] or "",
                        accession_number=record["accession_number"] or "",
                    )
                    artifact.score += 1.0
                    self._apply_neighbors(artifact, record["neighbors"] or [])
                    candidates[object_id] = artifact

        return sorted(candidates.values(), key=lambda item: item.score, reverse=True)[:limit]

    def get_related_artifacts(self, object_id: str, limit: int | None = None) -> list[Artifact]:
        limit = limit or settings.result_limit
        with self.driver.session() as session:
            records = session.run(
                """
                MATCH (a:Artifact {object_id: $object_id})--(shared)--(related:Artifact)
                WHERE related.object_id <> a.object_id
                WITH related,
                     collect(DISTINCT labels(shared)) AS shared_labels,
                     collect(DISTINCT coalesce(shared.name, shared.value, '')) AS shared_names,
                     count(DISTINCT shared) AS score
                OPTIONAL MATCH (related)--(ctx)
                RETURN related.object_id AS object_id,
                       related.title AS title,
                       related.description AS description,
                       related.dimensions AS dimensions,
                       related.accession_number AS accession_number,
                       score,
                       shared_names,
                       collect(DISTINCT {
                           labels: labels(ctx),
                           name: coalesce(ctx.name, ctx.value, ctx.url, '')
                       }) AS neighbors
                ORDER BY score DESC, title ASC
                LIMIT $limit
                """,
                object_id=object_id,
                limit=limit,
            )

            related = []
            for record in records:
                artifact = Artifact(
                    object_id=record["object_id"] or "",
                    title=record["title"] or "",
                    description=record["description"] or "",
                    dimensions=record["dimensions"] or "",
                    accession_number=record["accession_number"] or "",
                    score=float(record["score"] or 0),
                )
                self._apply_neighbors(artifact, record["neighbors"] or [])
                related.append(artifact)
            return related

    def _apply_neighbors(self, artifact: Artifact, neighbors: list[dict]) -> None:
        values: dict[str, list[str]] = defaultdict(list)
        for item in neighbors:
            labels = item.get("labels") or []
            name = item.get("name") or ""
            if not name or name == "unknown":
                continue
            for label in labels:
                field = LABEL_TO_FIELD.get(label)
                if field:
                    values[field].append(name)

        for field, items in values.items():
            unique_items = list(dict.fromkeys(items))
            joined = "、".join(unique_items[:5])
            if field == "image_url":
                setattr(artifact, field, unique_items[0] if unique_items else "")
            else:
                setattr(artifact, field, joined)
