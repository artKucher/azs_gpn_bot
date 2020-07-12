from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot, Update
from telegram.ext import CallbackContext, Updater, MessageHandler, Filters, CommandHandler
from telegram.utils.request import Request
from app.models import User


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
def do_command(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    reply_text = f"your id = {chat_id}"

    user, created = User.objects.get_or_create(
        external_id=chat_id,
        defaults={'username': update.message.from_user.username}
    )

    print('ere')
    update.message.reply_text(
        text = reply_text
    )

@log_errors
def do_count(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    user, created = User.objects.get_or_create(
        external_id=chat_id,
        defaults={'username': update.message.from_user.username}
    )

    count = 'logic'
    update.message.reply_text(
        text = f'Message {count}'
    )


class Command(BaseCommand):
    help = 'telegram bot'

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=settings.TOKEN,
            base_url=settings.PROXY_URL,
        )
        print(bot.get_me())

        updater = Updater(
            bot=bot,
            use_context=True,
        )
        message_handler2 = CommandHandler('count', do_count)
        updater.dispatcher.add_handler(message_handler2)
        message_handler = MessageHandler(Filters.text, do_command)
        updater.dispatcher.add_handler(message_handler)

        updater.start_polling()
        updater.idle()