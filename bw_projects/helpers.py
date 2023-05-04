"""Helper classes for the bw_projects."""
from typing import ClassVar, List

from peewee import Model, SqliteDatabase


class DatabaseHelper:
    """Helper class for database operations."""

    sqlite_database: ClassVar[SqliteDatabase] = SqliteDatabase(None)

    @classmethod
    def init_db(cls, database_name: str, tables: List[Model]) -> None:
        """Initializes the database."""
        cls.sqlite_database.init(database_name)
        cls.sqlite_database.create_tables(tables)
