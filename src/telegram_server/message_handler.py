from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, CommandHandler, MessageHandler as TelegramMessageHandler, filters

from src.common.interfaces import Message, ServiceConnector
from src.telegram_server.button_texts import ButtonText
import logging

# Define states for the conversation
MENU, PORTFOLIO, ANALYZE, RECOMMEND = range(4)

class MessageHandler:
    def __init__(self, connector: ServiceConnector):
        self.connector = connector
        self.keyboard = ButtonText.get_keyboard_layout()
        self.markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text, callback_data=text) for text in row] for row in self.keyboard]
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info("MessageHandler initialized")
        self.logger.info(f"Keyboard layout: {self.keyboard}")
        self.logger.info(f"Markup: {self.markup}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "Welcome to the Investment Bot! Here are the available commands:\n\n"
            "- Portfolio: View your investment portfolio.\n"
            "- Analyze: Get an analysis of current market conditions.\n"
            "- Recommend: Receive investment recommendations based on market trends.\n\n"
            "Please choose an option:"
        )
        await update.message.reply_text(help_text, reply_markup=self.markup)
        return MENU

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = ("Here are the available commands:\n\n"
            "- Portfolio: View your investment portfolio.\n"
            "- Analyze: Get an analysis of current market conditions.\n"
            "- Recommend: Receive investment recommendations based on market trends.\n\n"
            "Please choose an option:"
        )
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.reply_text(help_text, reply_markup=self.markup)
        else:
            await update.message.reply_text(help_text, reply_markup=self.markup)
        return MENU

    async def portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.message.reply_text("Fetching your portfolio...")
        response = await self.connector.send_request(
            "process_message",
            {
                "user_id": str(update.effective_user.id),
                "content": "Portfolio",
                "llm_type": "",
            },
        )
        await update.callback_query.message.reply_text(
            response.get("message", "Failed to fetch portfolio"),
            reply_markup=self.markup,
        )
        return ConversationHandler.END

    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.message.reply_text("Analyzing market conditions...")
        response = await self.connector.send_request(
            "process_message",
            {
                "user_id": str(update.effective_user.id),
                "content": "Analyze current market conditions and provide insight into trends",
                "llm_type": "",
            },
        )
        await update.callback_query.message.reply_text(
            response.get("message", "Failed to analyze market conditions"),
            reply_markup=self.markup,
        )
        return ConversationHandler.END

    async def recommend(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.message.reply_text("Generating investment recommendations...")
        response = await self.connector.send_request(
            "process_message",
            {
                "user_id": str(update.effective_user.id),
                "content": "Provide investment recommendations according to the current state of the market trends. As a result give a broad overview of the market based on the latest news and in the end add a list with the recomendation what should be bought and what should be avoided and other recomendations you found useful. While giving recomendation return the brief news summary and make sure that you provide the symbols of the stocks (crypto) you recommend. Recommend only reflecting by the news and not by your own knowledge.",
                "llm_type": "",
            },
        )
        await update.callback_query.message.reply_text(
            response.get("message", "Failed to generate recommendations"),
            reply_markup=self.markup,
        )
        return ConversationHandler.END

    async def button_click(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        self.logger.info(f"Button clicked: {query.data}")
        await query.answer()
        await query.message.edit_reply_markup(reply_markup=None)
        if query.data == ButtonText.PORTFOLIO:
            return await self.portfolio(update, context)
        elif query.data == ButtonText.ANALYZE:
            return await self.analyze(update, context)
        elif query.data == ButtonText.RECOMMEND:
            return await self.recommend(update, context)
        elif query.data == ButtonText.MENU:
            return await self.menu(update, context)
        return MENU

    def get_conversation_handler(self):
        return ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                MENU: [CallbackQueryHandler(self.button_click)],
                PORTFOLIO: [CallbackQueryHandler(self.button_click)],
                ANALYZE: [CallbackQueryHandler(self.button_click)],
                RECOMMEND: [CallbackQueryHandler(self.button_click)],
            },
            fallbacks=[CommandHandler('menu', self.menu)]
        )
