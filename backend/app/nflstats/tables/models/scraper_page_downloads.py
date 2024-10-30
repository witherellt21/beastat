import datetime
import json

from peewee import CharField, DateTimeField, IntegerField
from playhouse.postgres_ext import BinaryJSONField
from pydantic import BaseModel as BaseSerializer
from scrapp.db import DB
from scrapp.db.models import BaseModel
from scrapp.tables import BaseTable


class ScraperPageDownload(BaseModel):
    page_name = CharField()
    query_args = BinaryJSONField(dumps=json.dumps)
    