import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from telegram.ext import (
    Application,
)
from telegram import Bot
import uvicorn
from threading import Thread

from src.telegram_server.connectors import ClientServiceConnector
from src.telegram_server.message_handler import MessageHandler


class MessageRequest(BaseModel):
    chat_id: int
    message: str


class IvanTelegramBot:
    def __init__(self):
        load_dotenv()
        
        logging.basicConfig(level=logging.INFO)  # Add logging configuration

        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.connector = ClientServiceConnector(base_url=os.getenv("CLIENT_SERVICE_URL", "http://client:8000"))
        self.message_handler = MessageHandler(self.connector)
        self.bot = None
        self.app = FastAPI()
        self.setup_http_endpoints()
        
        logging.info("IvanTelegramBot initialized")  # Log initialization

    def setup_http_endpoints(self):
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
        """Send a message to a specific chat ID"""
        if self.bot is None:
            self.bot = Bot(token=self.token)
        await self.bot.send_message(chat_id=chat_id, text=message)

    async def post_init(self, application: Application):
        """Post initialization hook to setup bot commands"""
        self.bot = application.bot

    def setup_handlers(self, app: Application):
        # Register conversation handler
        conversation_handler = self.message_handler.get_conversation_handler()
        app.add_handler(conversation_handler)

    def run_http_server(self):
        """Run the FastAPI server"""
        uvicorn.run(self.app, host="0.0.0.0", port=8002)

    def run(self):
        # Start the FastAPI server in a separate thread
        http_thread = Thread(target=self.run_http_server, daemon=True)
        http_thread.start()

        # Run the Telegram bot
        app = Application.builder().token(self.token).post_init(self.post_init).build()
        self.setup_handlers(app)
        app.run_polling()


if __name__ == "__main__":
    bot = IvanTelegramBot()
    bot.run()
