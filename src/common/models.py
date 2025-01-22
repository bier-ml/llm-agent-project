"""
Database models using Tortoise ORM for user and news data persistence.
"""

from tortoise import fields
from tortoise.models import Model


class User(Model):
    """
    User model storing Telegram user information and portfolio preferences.

    Attributes:
        telegram_id: Unique Telegram user identifier
        portfolio: JSON field storing list of coin/stock symbols
        created_at: Timestamp of user creation
        updated_at: Timestamp of last update
    """

    telegram_id = fields.BigIntField(pk=True)
    portfolio = fields.JSONField(default=list)  # List of coin symbols
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class News(Model):
    """
    News model for storing financial news articles.

    Attributes:
        id: Unique news article identifier
        title: Article title
        content: Full article content
        created_at: Timestamp when article was added
    """

    id = fields.IntField(pk=True)
    title = fields.TextField()
    content = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
