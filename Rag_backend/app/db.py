from contextlib import contextmanager

import pymysql
from neo4j import GraphDatabase

from app.config import settings


class Database:
    def __init__(self) -> None:
        self._neo4j_driver = GraphDatabase.driver(
            settings.neo4j.uri,
            auth=(settings.neo4j.user, settings.neo4j.password),
        )

    @property
    def neo4j(self):
        return self._neo4j_driver

    @contextmanager
    def mysql_connection(self):
        conn = pymysql.connect(
            host=settings.mysql.host,
            port=settings.mysql.port,
            user=settings.mysql.user,
            password=settings.mysql.password,
            database=settings.mysql.database,
            charset=settings.mysql.charset,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute("SET NAMES utf8mb4")
            yield conn
        finally:
            conn.close()

    def close(self) -> None:
        self._neo4j_driver.close()
