from app.db import Database
from app.models import Artifact


class MySQLRetriever:
    def __init__(self, db: Database) -> None:
        self.db = db

    def get_artifact(self, object_id: str) -> Artifact | None:
        query = """
            SELECT a.object_id, a.title, a.period, a.type, a.material,
                   a.description, a.dimensions, a.image_url,
                   a.credit_line, a.accession_number,
                   m.name AS museum_name, m.name_cn AS museum_name_cn,
                   m.website AS museum_website
            FROM artifact a
            LEFT JOIN museum m ON a.museum_id = m.object_id
            WHERE a.object_id = %s AND a.is_deleted = 0
            LIMIT 1
        """
        with self.db.mysql_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (object_id,))
                row = cursor.fetchone()

        if not row:
            return None
        return Artifact(
            object_id=row.get("object_id") or "",
            title=row.get("title") or "",
            period=row.get("period") or "",
            material=row.get("material") or "",
            artifact_type=row.get("type") or "",
            museum=row.get("museum_name_cn") or row.get("museum_name") or "",
            description=row.get("description") or "",
            dimensions=row.get("dimensions") or "",
            image_url=row.get("image_url") or "",
            museum_url=row.get("museum_website") or "",
            accession_number=row.get("accession_number") or "",
        )
