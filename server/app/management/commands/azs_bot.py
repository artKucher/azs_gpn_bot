from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot, Update
from telegram.ext import CallbackContext, Updater, MessageHandler, Filters, CommandHandler
from telegram.utils.request import Request
from app.models import User
from app.tgbot.azs_telegram_bot import AzsBot

class Command(BaseCommand):
    help = 'telegram bot'

    def handle(self, *args, **options):
        bot = AzsBot()
        bot.start()