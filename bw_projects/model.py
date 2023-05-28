"""Model classes for bw_projects."""
import json
from typing import Dict

from peewee import Model, SqliteDatabase, TextField
from playhouse.sqlite_ext import JSONField

SQLITE_DATABASE: SqliteDatabase = SqliteDatabase(None)


def _attributes_dumps(value: Dict[str, str]) -> str:
    if value is not None and not isinstance(value, Dict):
        raise TypeError(value)
    return json.dumps(value)


class BaseModel(Model):
    """Base model class for all models."""

    class Meta:
        """Meta class for all models."""

        database = SQLITE_DATABASE


class Project(BaseModel):
    """Project model class."""

    name = TextField(index=True, unique=True)
    dir_data = TextField()
    dir_logs = TextField()
    attributes = JSONField(json_dumps=_attributes_dumps)

    def __lt__(self, other):
        return self.name < other.name
