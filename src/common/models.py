from tortoise import fields
from tortoise.models import Model


class User(Model):
    telegram_id = fields.BigIntField(pk=True)
    portfolio = fields.JSONField(default=list)  # List of coin symbols
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class News(Model):
    id = fields.IntField(pk=True)
    title = fields.TextField()
    content = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
