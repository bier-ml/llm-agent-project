from textwrap import dedent

from telegram import BotCommand, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.common.interfaces import ServiceConnector
from src.telegram_server.button_texts import ButtonText


class CommandRegistry:
    def __init__(self, connector: ServiceConnector):
        self.connector = connector
        self.keyboard = ButtonText.get_keyboard_layout()
        self.markup = ReplyKeyboardMarkup(self.keyboard, resize_keyboard=True)

        # Define commands for menu button
        self.commands = [
            BotCommand("help", ButtonText.DESC_HELP),
            BotCommand("portfolio", ButtonText.DESC_PORTFOLIO),
            BotCommand("analyze", ButtonText.DESC_ANALYZE),
            BotCommand("recommend", ButtonText.DESC_RECOMMEND),
        ]

    async def setup_commands(self, application):
        """Set up the bot commands in Telegram"""
        await application.bot.set_my_commands(self.commands)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Hello! I'm IVAN, your Interactive Venture Analysis Network. "
            "I can help you manage your financial portfolio and provide investment recommendations.",
            reply_markup=self.markup,
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = dedent(
            """
            Available commands:
            /help - Show this help message
            /portfolio - View your portfolio
            /analyze - Analyze market conditions
            /recommend - Get investment recommendations
            """
        )
        await update.message.reply_text(help_text, reply_markup=self.markup)

    async def portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Fetching your portfolio...", reply_markup=self.markup
        )
        # Add actual portfolio logic here using self.connector

    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Analyzing market conditions...", reply_markup=self.markup
        )
        # Add market analysis logic here using self.connector

    async def recommend(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Generating investment recommendations...", reply_markup=self.markup
        )
        # Add recommendation logic here using self.connector

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        menu_text = dedent(f"""
            📋 Available Commands:
            ❓ /help - Show help message
            {ButtonText.PORTFOLIO} - View your portfolio
            {ButtonText.ANALYZE} - Analyze market conditions
            {ButtonText.RECOMMEND} - Get investment recommendations
        """)
        await update.message.reply_text(menu_text, reply_markup=self.markup)

    def get_handlers(self):
        return {
            "start": self.start,
            "help": self.help,
            "menu": self.menu,
            "portfolio": self.portfolio,
            "analyze": self.analyze,
            "recommend": self.recommend,
        }
