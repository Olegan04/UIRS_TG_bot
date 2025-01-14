from aiogram import Bot
from bot.config import parse_settings

settings = parse_settings()
bot = Bot(token=settings.bot_token.get_secret_value())