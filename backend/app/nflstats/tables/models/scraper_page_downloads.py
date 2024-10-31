import json
from datetime import datetime

from peewee import CharField, DateTimeField
from playhouse.postgres_ext import BinaryJSONField, JSONField
from pydantic import BaseModel as BaseSerializer
from scrapp.db.models import BaseModel
from scrapp.tables import BaseTable


class ScraperPageDownload(BaseModel):
    page_name = CharField()
    query_args = CharField()  # A string representation of JSON data
    # query_args = JSONField(dumps=json.dumps)
    tables = BinaryJSONField(dumps=json.dumps)
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        indexes = ((("page_name", "query_args"), True),)


class ScraperPageDownloadSerializer(BaseSerializer):
    page_name: str
    query_args: str
    tables: list[str]
    timestamp: datetime


class ScraperPageDownloadsTable(BaseTable):
    MODEL_CLASS = ScraperPageDownload
    SERIALIZER_CLASS = ScraperPageDownloadSerializer
    READ_SERIALIZER_CLASS = ScraperPageDownloadSerializer
    PKS = ["page_name", "query_args"]
