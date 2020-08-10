
from django.conf import settings
from telegram import Bot
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from telegram.utils.request import Request

from backend.settings import FILTERS_COUNT
from app.models import User, GasStationProperties

from .edit_filters_menu import add_filter_menu, tune_filters_menu, choose_filter, submit_fuel_type, \
    select_filter_property, change_filter_name, change_filter_radius, change_target_fuel
from .find_gas_station import *
from .fuel_price_statistic import *
from .choose_active_filter_menu import *
from .keyboards import edit_filter_keyboard
from .main_menu import *
import logging as log

log.basicConfig(filename="sample.log", level=log.INFO)

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

    #/help command
    @log_errors
    def do_help(self, update: Update, context: CallbackContext):
        help_message='/start - Начать работу с ботом\n' \
                     '/help - Показать подсказку\n\n' \
                     'Фильтр\n' \
                     f'Каждый пользователь может создать {FILTERS_COUNT} шт. фильтров. ' \
                     f'На основе параметров активного фильтра подбираются подходящие АЗС для пользователя. ' \
                     f'Для настройки фильтра нажмите кнопку "Настроить фильтры" и выберите фильтр. ' \
                     f'Выберите опции, которыми должна обладать АЗС. ' \
                     f'Смените название фильтра нажав на соответствующую кнопку. ' \
                     f'В названии фильтра обязательно должны присутствовать буквы в начале. ' \
                     f'Для смены радиуса поиска азс нажмите на соответствующую кнопку и введите целое число в км. ' \
                     f'На основе выбранного топлива происходит сортировка азс по выгодности, а также вывод графиков цены на топливо. ' \
                     f'После окончания редактирования фильтра нажмите кнопку "Главное меню"\n\n' \
                     f'Подбор АЗС\n' \
                     f'Для подбора подходящей АЗС создайте и выберите активный фильтр. ' \
                     f'Отправьте боту свою геолокация. ' \
                     f'На основе активного фильтра будут подобраны азс и отсортированны по цене топлива по возрастанию. ' \
                     f'Выберите желаемую азс и бот отправит вам маршрут до неё\n\n' \
                     f'Динамика цен\n' \
                     f'Нажмите на соответствующую кнопку в главном меню и выберите интересующую АЗС для просмотра ' \
                     f'графика изменения цены на топливо, выбранного в активном фильтре.'

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=help_message
        )
        main_menu(update,context,new=True)

    #/start command
    @log_errors
    def do_start(self, update: Update, context: CallbackContext):
        main_menu(update, context, new=True)

    #bot recieved digit
    @log_errors
    def do_digit_command(self, update: Update, context: CallbackContext):
        log.info("Цифра-команда")
        chat_id = update.message.chat_id
        context.user_data['user_id'] = chat_id
        filter = context.user_data['editable_filter']
        if filter:
            if context.user_data['editable_field'] == 'radius':
                context.user_data['editable_field'] = None
                radius = update.message.text
                print(radius)
                setattr(filter, 'search_radius', radius)
                filter.save()
                update.message.reply_text(
                    text=f"Для фильтра '{filter.name}' установлен радиус поиска: {radius}",
                    reply_markup=edit_filter_keyboard(context)
                )
        else:
            update.message.reply_text(
                text=update.callback_query.text
            )

    #bot recieved text
    @log_errors
    def do_text_command(self, update: Update, context: CallbackContext):
        log.info("Текст-команда")
        chat_id = update.message.chat_id
        context.user_data['user_id'] = chat_id
        filter = context.user_data['editable_filter']
        if filter:
            if context.user_data['editable_field'] == 'name':
                context.user_data['editable_field'] = None
                previous_name = filter.name
                setattr(filter, 'name', update.message.text)
                filter.save()
                update.message.reply_text(
                    text=f"Для фильтра '{previous_name}' установлено новое имя: {filter.name}",
                    reply_markup=edit_filter_keyboard(context)
                )
        else:
            print(update)
            update.message.reply_text(
                text=update.message.text
            )

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
        self.updater.dispatcher.add_handler(CommandHandler('help', self.do_help))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'^\d+$'), self.do_digit_command))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'\w+'), self.do_text_command))

        self.updater.dispatcher.add_handler(CallbackQueryHandler(main_menu, pattern='main'))

        #find gas station
        self.updater.dispatcher.add_handler(MessageHandler(Filters.location, filtered_gas_stations))
        self.updater.dispatcher.add_handler(
            CallbackQueryHandler(submit_target_gas_station, pattern=r'targetgasstation_\d+'))
        #choose active filter
        self.updater.dispatcher.add_handler(
            CallbackQueryHandler(choose_active_filter, pattern='choose_active_filter'))
        self.updater.dispatcher.add_handler(
            CallbackQueryHandler(submit_active_filter, pattern=r'activefilter_\d+'))
        #edit filter
        self.updater.dispatcher.add_handler(CallbackQueryHandler(add_filter_menu, pattern='m1_add_filter'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(tune_filters_menu, pattern='tune_filters'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(choose_filter, pattern=r'editfilter_\d+'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(change_filter_name, pattern='change_filter_name'))
        self.updater.dispatcher.add_handler(
            CallbackQueryHandler(change_filter_radius, pattern='change_filter_radius'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(change_target_fuel, pattern='change_target_fuel'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(submit_fuel_type, pattern=r'fueltype_\w+'))
        for property in GasStationProperties._meta.get_fields():
            self.updater.dispatcher.add_handler(
                CallbackQueryHandler(select_filter_property, pattern=property.name))
        #price statistic
        self.updater.dispatcher.add_handler(CallbackQueryHandler(price_statistic, pattern='price_statistic'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(submit_price_statistic, pattern=r'pricestatistic_\w+'))

        self.updater.start_polling()
        self.updater.idle()
