from typing import Any, Callable, Dict

from telegram import Update
from telegram.ext import ContextTypes

from src.common.interfaces import ServiceConnector


class CommandRegistry:
    def __init__(self, connector: ServiceConnector):
        self.connector = connector
        self._handlers = self._register_handlers()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Hello! I'm IVAN, your Interactive Venture Analysis Network. "
            "I can help you manage your financial portfolio and provide investment recommendations."
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
        Available commands:
        /start - Start the bot
        /help - Show this help message
        /portfolio - Show your current portfolio
        /analyze - Analyze market trends
        /recommend - Get investment recommendations
        """
        await update.message.reply_text(help_text)

    def _register_handlers(self) -> Dict[str, Callable]:
        return {
            "start": self.start_command,
            "help": self.help_command,
        }

    def get_handlers(self) -> Dict[str, Callable]:
        return self._handlers
