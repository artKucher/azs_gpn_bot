from telegram import Update
from telegram.ext import CallbackContext
from app.models import User, Filter, FUEL_DICT
from app.tgbot.keyboards import tune_filters_keyboard, edit_filter_keyboard, choose_fuel_type_keyboard
from backend.settings import FILTERS_COUNT
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

#choose filter for editing
@log_errors
def choose_filter(update: Update, context: CallbackContext):
    log.info("ВЫБОР ФИЛЬТРА ДЛЯ РЕДАКТИРОВАНИЯ")
    chat_id = update.effective_user['id']

    context.user_data['user_id'] = chat_id
    filter_id = update.callback_query.data.split('_')[-1]
    filter = Filter.objects.get(id=filter_id)
    context.user_data['editable_filter'] = filter
    edit_filter_menu(update, context)

#choose filter or add filter menu
@log_errors
def tune_filters_menu(update: Update, context: CallbackContext):
    log.info('РЕДАКТИРОВАНИЕ ФИЛЬТРОВ')
    chat_id = update.effective_user['id']
    user, created = User.objects.get_or_create(
        external_id=chat_id,
        defaults={'username': update.effective_user['username']}
    )
    filters = Filter.objects.filter(user=user)[:FILTERS_COUNT]
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Выберите фильтр для редактирования:',
        reply_markup=tune_filters_keyboard(filters))

#add filter menu
@log_errors
def add_filter_menu(update: Update, context: CallbackContext,new=False):
    log.info('ДОБАВИТЬ ФИЛЬТР')
    chat_id = update.effective_user['id']
    user, created = User.objects.get_or_create(
        external_id=chat_id,
        defaults={'username': update.effective_user['username']}
    )
    new_filter = Filter(user=user)
    new_filter.save()
    context.user_data['editable_filter'] = new_filter
    edit_filter_menu(update, context, new)

@log_errors
def edit_filter_menu(update: Update, context: CallbackContext, new=False):
    log.info('ОТРЕДАКТИРОВАТЬ ФИЛЬТР')
    filter = context.user_data['editable_filter']
    text = f'Редактирование фильтра "{filter.name}"'
    reply_markup = edit_filter_keyboard(context)
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
def select_filter_property(update: Update, context: CallbackContext):
    filter = context.user_data['editable_filter']
    property = update.callback_query.data
    # меняем значение проперти на противоположное
    setattr(filter, property, not getattr(filter, property))
    filter.save()

    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text=f'Опция "{filter._meta.get_field(property).verbose_name}"',
        reply_markup=edit_filter_keyboard(context)
    )

@log_errors
def change_filter_radius(update: Update, context: CallbackContext):
    context.user_data['editable_field'] = 'radius'

    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text=f'Введите радиус поиска в километрах'
    )

@log_errors
def change_filter_name(update: Update, context: CallbackContext):
    filter = context.user_data['editable_filter']
    context.user_data['editable_field'] = 'name'

    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text=f'Введите новое имя для фильтра \"{filter.name}\" (буквы обязательно).'
    )


@log_errors
def change_target_fuel(update: Update, context: CallbackContext):
    log.info("СМЕНИТЬ ТИП БЕНЗИНА")
    context.user_data['editable_field'] = 'target_fuel'
    fuel_types = [(k, v) for k, v in FUEL_DICT.items()]
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text=f'Выберете тип топлива, которым заправляете авто',
        reply_markup=choose_fuel_type_keyboard(fuel_types)
    )


@log_errors
def submit_fuel_type(update: Update, context: CallbackContext):
    log.info("ВЫБОР ТИПА БЕНЗИНА")
    chat_id = update.effective_user['id']
    context.user_data['user_id'] = chat_id
    filter = context.user_data['editable_filter']

    fuel_type = update.callback_query.data.split('_')[-1]
    setattr(filter, 'target_fuel', fuel_type)
    filter.save()
    main_menu(update, context)