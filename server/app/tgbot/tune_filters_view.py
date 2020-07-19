from django.conf import settings
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, Updater, MessageHandler, Filters, CommandHandler
from telegram.utils.request import Request
from app.models import User, Filter
from backend.settings import FILTERS_COUNT
from .azs_telegram_bot import AzsBot


class start_view(AzsBot):
    def log_errors(f):
        def inner(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                error_message = f'ОШИБКА {e}'
                print(error_message)
                raise e

        return inner

    @log_errors
    def draw_tune_filters_menu(self, fil):
        custom_keyboard = [['Показать заправки(фильтр: )'],['Выбрать фильтр', self.commands['tune_filters']]]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard)
        return reply_markup

    @log_errors
    def do_tune_filters(self, update: Update):
        chat_id = update.message.chat_id
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.message.from_user.username}
        )
        filters = Filter.objects.filter(user=user)[:FILTERS_COUNT]
        if filters.count() == 0:
            print('Нет фильтров')