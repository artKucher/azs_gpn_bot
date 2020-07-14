from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot, Update
from telegram.ext import CallbackContext, Updater, MessageHandler, Filters, CommandHandler
from telegram.utils.request import Request
from app.models import User, GasStation
from app.tgbot.azs_telegram_bot import AzsBot

class Command(BaseCommand):
    help = 'fill database'

    def handle(self, *args, **options):
        for i in range(0,2):
            flags = [randint(0,1) for i in range(26)]
            print(flags)
            GasStation(number=randint(9999), gps=Point(random.uniform(1.5, 1.9),random.uniform(1.5, 1.9)), **flags).save()