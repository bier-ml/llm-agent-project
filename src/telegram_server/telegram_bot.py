import os
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler as TelegramMessageHandler,
    filters,
)

from src.telegram_server.command_handlers import CommandRegistry
from src.telegram_server.connectors import ClientServiceConnector
from src.telegram_server.message_handler import MessageHandler


class IvanTelegramBot:
    def __init__(self):
        load_dotenv()

        self.token = os.getenv("TELEGRAM_TOKEN")
        self.connector = ClientServiceConnector(
            base_url=os.getenv("CLIENT_SERVICE_URL", "http://client:8000")
        )
        self.command_registry = CommandRegistry(self.connector)
        self.message_handler = MessageHandler(self.connector, self.command_registry)

    async def post_init(self, application: Application):
        """Post initialization hook to setup bot commands"""
        await self.command_registry.setup_commands(application)

    def setup_handlers(self, app: Application):
        # Register command handlers
        for command, handler in self.command_registry.get_handlers().items():
            app.add_handler(CommandHandler(command, handler))

        # Register message handler
        app.add_handler(
            TelegramMessageHandler(
                filters.TEXT & ~filters.COMMAND, self.message_handler.handle
            )
        )

    def run(self):
        app = Application.builder().token(self.token).post_init(self.post_init).build()
        self.setup_handlers(app)
        app.run_polling()


if __name__ == "__main__":
    bot = IvanTelegramBot()
    bot.run()
