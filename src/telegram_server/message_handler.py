from telegram import Update
from telegram.ext import ContextTypes

from src.common.interfaces import Message, ServiceConnector
from src.telegram_server.button_texts import ButtonText
from src.telegram_server.command_handlers import CommandRegistry


class MessageHandler:
    def __init__(self, connector: ServiceConnector, command_registry: CommandRegistry):
        self.connector = connector
        self.command_registry = command_registry
        self.text_to_handler = {
            ButtonText.HELP: command_registry.help,
            ButtonText.PORTFOLIO: command_registry.portfolio,
            ButtonText.ANALYZE: command_registry.analyze,
            ButtonText.RECOMMEND: command_registry.recommend,
        }

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        # Check if the message is a button press
        if text in self.text_to_handler:
            await self.text_to_handler[text](update, context)
            return

        # Handle regular messages
        message = Message(
            user_id=user_id,
            content=text,
            metadata={"chat_id": chat_id},
        )
        response = await self.connector.send_request("process_message", message.__dict__)
        await update.message.reply_text(response["message"], reply_markup=self.command_registry.markup)
