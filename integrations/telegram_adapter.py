import os
import logging

logger = logging.getLogger("telegram_adapter")


def send_alert(chat_id: str, message: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not configured; alert skipped")
        return False
    try:
        import telebot

        bot = telebot.TeleBot(token)
        bot.send_message(chat_id, message)
        return True
    except Exception as e:
        logger.exception("Failed to send telegram alert")
        return False
