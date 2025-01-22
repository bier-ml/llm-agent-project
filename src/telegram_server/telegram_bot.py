import logging
import os
from threading import Thread

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from telegram import Bot
from telegram.ext import Application

from src.telegram_server.connectors import ClientServiceConnector
from src.telegram_server.message_handler import MessageHandler


class MessageRequest(BaseModel):
    """Request model for sending messages via the HTTP endpoint."""

    chat_id: int
    message: str


class IvanTelegramBot:
    """
    Main Telegram bot class that handles both Telegram webhook events and HTTP requests.

    This bot serves two purposes:
    1. Processes incoming Telegram messages through a conversation handler
    2. Provides an HTTP endpoint for other services to send messages to Telegram chats
    """

    def __init__(self):
        """Initialize bot components and configurations."""
        load_dotenv()
        logging.basicConfig(level=logging.INFO)

        # Core components initialization
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.connector = ClientServiceConnector(base_url=os.getenv("CLIENT_SERVICE_URL", "http://client:8000"))
        self.message_handler = MessageHandler(self.connector)

        # FastAPI setup for HTTP endpoints
        self.bot = None
        self.app = FastAPI()
        self.setup_http_endpoints()

        logging.info("IvanTelegramBot initialized")

    def setup_http_endpoints(self):
        """Configure FastAPI endpoints for external message sending."""

        @self.app.post("/send_message")
        async def send_message(request: MessageRequest):
            if self.bot is None:
                raise HTTPException(status_code=500, detail="Bot not initialized")
            try:
                await self.send_message(request.chat_id, request.message)
                return {"status": "success"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    async def send_message(self, chat_id: int, message: str):
        """
        Send a message to a specific Telegram chat.

        Args:
            chat_id: Telegram chat identifier
            message: Text message to send
        """
        if self.bot is None:
            self.bot = Bot(token=self.token)
        await self.bot.send_message(chat_id=chat_id, text=message)

    async def post_init(self, application: Application):
        """
        Post-initialization hook called after the Application is fully initialized.

        Args:
            application: Telegram Application instance
        """
        self.bot = application.bot

    def setup_handlers(self, app: Application):
        """
        Configure message handlers for the Telegram bot.

        Args:
            app: Telegram Application instance
        """
        conversation_handler = self.message_handler.get_conversation_handler()
        app.add_handler(conversation_handler)

    def run_http_server(self):
        """Start the FastAPI server for handling HTTP requests."""
        uvicorn.run(self.app, host="0.0.0.0", port=8002)

    def run(self):
        """
        Start both the HTTP server and Telegram bot.

        The HTTP server runs in a separate daemon thread while the main thread
        handles the Telegram bot polling.
        """
        # Start HTTP server in background thread
        http_thread = Thread(target=self.run_http_server, daemon=True)
        http_thread.start()

        # Configure and start Telegram bot
        app = Application.builder().token(self.token).post_init(self.post_init).build()
        self.setup_handlers(app)
        app.run_polling()


if __name__ == "__main__":
    bot = IvanTelegramBot()
    bot.run()
