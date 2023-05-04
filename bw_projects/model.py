"""Model classes for the bw_projects."""
from peewee import Model, TextField
from playhouse.sqlite_ext import JSONField

from .helpers import DatabaseHelper


class BaseModel(Model):
    """Base model class for all models."""

    class Meta:
        """Meta class for all models."""

        database = DatabaseHelper.sqlite_database


class Project(BaseModel):
    """Project model class."""

    name = TextField(index=True, unique=True)
    attributes = JSONField()
