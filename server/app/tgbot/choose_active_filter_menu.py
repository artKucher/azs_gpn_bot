from telegram import Update
from telegram.ext import CallbackContext
from app.models import User, Filter
from backend.settings import FILTERS_COUNT
from app.tgbot.keyboards import choose_active_filter_keyboard

from app.tgbot.edit_filters_menu import add_filter_menu
from app.tgbot.main_menu import main_menu
import logging as log

log.basicConfig(level=log.INFO)

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
def choose_active_filter(update: Update, context: CallbackContext, new=False):
    log.info('СПИСОК ФИЛЬТРОВ ДЛЯ ВЫБОРА АКТИВНОГО ФИЛЬТРА')
    chat_id = update.effective_user['id']
    user, created = User.objects.get_or_create(
        external_id=chat_id,
        defaults={'username': update.effective_user['username']}
    )
    filters = Filter.objects.filter(user=user)[:FILTERS_COUNT]
    if not filters.count():
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы не создали ни одного фильтра, время это исправить.'
        )
        add_filter_menu(update, context, new)
        return
    text = 'Выберите активный фильтр:'
    reply_markup = choose_active_filter_keyboard(filters)
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


@log_errors
def submit_active_filter(update: Update, context: CallbackContext):
    log.info("ВЫБОР АКТИВНОГО ФИЛЬТРА")
    chat_id = update.effective_user['id']
    user, created = User.objects.get_or_create(
        external_id=chat_id,
        defaults={'username': update.effective_user['username']}
    )
    context.user_data['user_id'] = chat_id
    filter_id = update.callback_query.data.split('_')[-1]
    filter = Filter.objects.get(id=filter_id)
    setattr(user, 'active_filter', filter)
    user.save()
    main_menu(update, context)

