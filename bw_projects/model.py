"""Model classes for bw_projects."""
from peewee import BooleanField, Model, SqliteDatabase, TextField
from playhouse.sqlite_ext import JSONField

SQLITE_DATABASE: SqliteDatabase = SqliteDatabase(None)


class BaseModel(Model):
    """Base model class for all models."""

    class Meta:
        """Meta class for all models."""

        database = SQLITE_DATABASE


class Project(BaseModel):
    """Project model class."""

    name = TextField(index=True, unique=True)
    attributes = JSONField()
    deleted = BooleanField(default=False)

    def __lt__(self, other):
        return self.name < other.name
