from django.conf import settings
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, Updater, MessageHandler, Filters, CommandHandler
from telegram.utils.request import Request
from app.models import User

class AzsBot():
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
    def do_command(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        text = update.message.text
        reply_text = f"your id = {chat_id}"

        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.message.from_user.username}
        )

        print('ere')
        update.message.reply_text(
            text=reply_text
        )

    @log_errors
    def do_count(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id

        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.message.from_user.username}
        )

        count = 'logic'
        update.message.reply_text(
            text=f'Message {count}'
        )

    @log_errors
    def do_start(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id

        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.message.from_user.username}
        )

        update.message.reply_text(
            text=f"Ok let's get it",
            reply_markup=self.draw_menu()
        )

    @log_errors
    def draw_menu(self):
        custom_keyboard = [['Показать заправки(фильтр: )'],['Выбрать фильтр', 'Настроить фильтры']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard)
        return reply_markup

    def __init__(self):
        self.request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        self.bot = Bot(
            request=self.request,
            token=settings.TOKEN,
            base_url=settings.PROXY_URL,
        )
        self.updater = Updater(
            bot=self.bot,
            use_context=True,
        )

    def start(self):
        self.updater.dispatcher.add_handler(CommandHandler('start', self.do_start))
        self.updater.dispatcher.add_handler(CommandHandler('count', self.do_count))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.do_command))

        self.updater.start_polling()
        self.updater.idle()

