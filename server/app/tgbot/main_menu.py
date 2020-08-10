from telegram import Update
from telegram.ext import CallbackContext
from app.tgbot.keyboards import main_menu_keyboard
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
#main menu
@log_errors
def main_menu(update: Update, context: CallbackContext, new=False):
    context.user_data['editable_filter'] = None

    chat_id = update.effective_user['id']
    user, created = User.objects.get_or_create(
        external_id=chat_id,
        defaults={'username': update.effective_user['username']}
    )
    context.user_data['user_id'] = chat_id

    active_filter = user.active_filter
    text = f'Главное меню. Aктивный фильтр{": " + active_filter.name if active_filter else " не выбран"}.\n' \
           f'Для подбора АЗС отправьте свою геолокацию.'
    reply_markup = main_menu_keyboard()
    if new:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=reply_markup
        )
    else:
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )