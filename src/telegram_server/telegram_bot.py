import os
from typing import Any, Dict

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.common.interfaces import Message, ServiceConnector
from src.telegram_server.command_handlers import CommandRegistry
from src.telegram_server.connectors import ClientServiceConnector


class IvanTelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.connector: ServiceConnector = ClientServiceConnector(
            base_url=os.getenv("CLIENT_SERVICE_URL", "http://client:8000")
        )
        self.command_registry = CommandRegistry(self.connector)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = Message(
            user_id=update.effective_user.id,
            content=update.message.text,
            metadata={"chat_id": update.effective_chat.id},
        )
        response = await self.connector.send_request(
            "process_message", message.__dict__
        )
        await update.message.reply_text(response["message"])

    def setup_handlers(self, app: Application):
        # Register command handlers
        for command, handler in self.command_registry.get_handlers().items():
            app.add_handler(CommandHandler(command, handler))

        # Register message handler
        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    def run(self):
        app = Application.builder().token(self.token).build()
        self.setup_handlers(app)
        app.run_polling()


if __name__ == "__main__":
    bot = IvanTelegramBot()
    bot.run()
