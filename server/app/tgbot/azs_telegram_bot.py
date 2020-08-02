import io
import operator
from datetime import timedelta

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.db.models import Prefetch, Min, Max, F, Q, Subquery, OuterRef, Count, Avg
from django.utils.datetime_safe import datetime
from telegram import Bot, Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from telegram.utils.request import Request
from app.models import User, Filter, GasStationProperties, GasStation, FUEL_DICT, FUEL_CHOICES, FuelPrice
from app.tgbot.keyboards import choose_fuel_type_keyboard, price_statistic_keyboard, choose_active_filter_keyboard, \
    edit_filter_keyboard, main_menu_keyboard, tune_filters_keyboard, choose_target_gas_station_keyboard
from backend.settings import FILTERS_COUNT
import matplotlib.pyplot as plt


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
    def do_help(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.message.from_user.username}
        )
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
        self.main_menu(update,context,new=True)

    @log_errors
    def do_start(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.message.from_user.username}
        )

        self.main_menu(update, context, new=True)

    @log_errors
    def filtered_gas_stations(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.message.from_user.username}
        )
        context.user_data['user_id'] = chat_id
        if not user.active_filter:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Сначала выберите активный фильтр'
            )
            self.choose_active_filter(update,context,new=True)
            return
        point = Point(update.message.location.latitude, update.message.location.longitude)
        context.user_data['user_location'] = point
        active_filter = user.active_filter

        filtered_property = {}
        for field in GasStationProperties._meta.get_fields():
            value = getattr(active_filter, field.name)
            if value:
                filtered_property[field.name] = value

        fuel_price_sq = Subquery(FuelPrice.objects.\
                    filter(gas_station=OuterRef('id')).\
                    filter(Q(fuel_type=active_filter.target_fuel) | Q(fuel_type__isnull=True)).\
                    order_by('-date').values('price')[:1])
        search_radius = active_filter.search_radius
        gas_stations = []
        for r in range(active_filter.search_radius, active_filter.search_radius*10):
            gas_stations = GasStation.objects.filter(
                location__distance_lt=(point, Distance(km=r)),
                **filtered_property). \
                annotate(price=fuel_price_sq).order_by('price')
            if gas_stations.count():
                break
            search_radius = r
        message = ('Выберите АЗС' if search_radius==active_filter.search_radius
                   else f'В радиусе {active_filter.search_radius} км. нет АЗС. '
                        f'Радиус поиска расширен до {search_radius} км.')
        update.message.reply_text(
            text=f"Выберите АЗС",
            reply_markup=choose_target_gas_station_keyboard(gas_stations)
        )

    @log_errors
    def do_digit_command(self, update: Update, context: CallbackContext):
        print("Цифра-команда")
        chat_id = update.message.chat_id
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.message.from_user.username}
        )
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

    @log_errors
    def do_text_command(self, update: Update, context: CallbackContext):
        print("Текст-команда")
        chat_id = update.message.chat_id
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.message.from_user.username}
        )
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

    @log_errors
    def choose_filter(self, update: Update, context: CallbackContext):
        print("ВЫБОР ФИЛЬТРА ДЛЯ РЕДАКТИРОВАНИЯ")
        chat_id = update.effective_user['id']
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.effective_user['username']}
        )
        context.user_data['user_id'] = chat_id
        filter_id = update.callback_query.data.split('_')[-1]
        filter = Filter.objects.get(id=filter_id)
        context.user_data['editable_filter'] = filter
        self.edit_filter_menu(update, context)

    @log_errors
    def main_menu(self, update: Update, context: CallbackContext, new=False):
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

    @log_errors
    def tune_filters_menu(self, update: Update, context: CallbackContext):
        print('РЕДАКТИРОВАНИЕ ФИЛЬТРОВ')
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

    @log_errors
    def add_filter_menu(self, update: Update, context: CallbackContext,new=False):
        print('ДОБАВИТЬ ФИЛЬТР')
        chat_id = update.effective_user['id']
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.effective_user['username']}
        )
        new_filter = Filter(user=user)
        new_filter.save()
        context.user_data['editable_filter'] = new_filter
        self.edit_filter_menu(update, context, new)

    @log_errors
    def edit_filter_menu(self, update: Update, context: CallbackContext, new=False):
        print('ОТРЕДАКТИРОВАТЬ ФИЛЬТР')
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
    def select_filter_property(self, update: Update, context: CallbackContext):
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
    def change_filter_radius(self, update: Update, context: CallbackContext):
        filter = context.user_data['editable_filter']
        context.user_data['editable_field'] = 'radius'
        property = update.callback_query.data

        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text=f'Введите радиус поиска в километрах'
        )

    @log_errors
    def change_filter_name(self, update: Update, context: CallbackContext):
        filter = context.user_data['editable_filter']
        context.user_data['editable_field'] = 'name'
        property = update.callback_query.data

        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text=f'Введите новое имя для фильтра \"{filter.name}\" (буквы обязательно).'
        )

    @log_errors
    def choose_active_filter(self, update: Update, context: CallbackContext, new=False):
        print('ВЫБОР АКТИВНОГО ФИЛЬТРА')
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
            self.add_filter_menu(update,context, new)
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
    def price_statistic(self, update: Update, context: CallbackContext):
        print('ВЫБОР АЗС СТАТИСТИКА')
        chat_id = update.effective_user['id']
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.effective_user['username']}
        )
        if not user.active_filter:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Сначала вам нужно выбрать активный фильтр.\n'
                     f'Топливо для отображения статистики будет выбрано на основе активного фильтра'
            )
            self.choose_active_filter(update,context,new=True)
            return
        gas_stations = GasStation.objects.all()
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text='Выберите станцию для просмотра динамики цены:',
            reply_markup=price_statistic_keyboard(gas_stations))

    @log_errors
    def submit_active_filter(self, update: Update, context: CallbackContext):
        print("ВЫБОР АКТИВНОГО ФИЛЬТРА")
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
        self.main_menu(update, context)

    @log_errors
    def change_target_fuel(self, update: Update, context: CallbackContext):
        print("СМЕНИТЬ ТИП БЕНЗИНА")
        filter = context.user_data['editable_filter']
        context.user_data['editable_field'] = 'target_fuel'
        fuel_types = [(k, v) for k, v in FUEL_DICT.items()]
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text=f'Выберете тип топлива, которым заправляете авто',
            reply_markup=choose_fuel_type_keyboard(fuel_types)
        )

    @log_errors
    def submit_fuel_type(self, update: Update, context: CallbackContext):
        print("ВЫБОР ТИПА БЕНЗИНА")
        chat_id = update.effective_user['id']
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.effective_user['username']}
        )
        context.user_data['user_id'] = chat_id
        filter = context.user_data['editable_filter']

        fuel_type = update.callback_query.data.split('_')[-1]
        setattr(filter, 'target_fuel', fuel_type)
        filter.save()
        self.main_menu(update, context)

    @log_errors
    def submit_target_gas_station(self, update: Update, context: CallbackContext):
        print("ВЫБОР ЦЕЛЕВОЙ ЗАПРАВКИ")
        chat_id = update.effective_user['id']
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.effective_user['username']}
        )
        context.user_data['user_id'] = chat_id
        gas_station_id = update.callback_query.data.split('_')[-1]
        gas_station = GasStation.objects.get(id=gas_station_id)
        gs_location = gas_station.location
        user_location = context.user_data['user_location']

        direct_message = f'https://www.google.ru/maps/dir/{user_location.x},{user_location.y}/{gs_location.x},{gs_location.y}/'
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=direct_message )
        self.main_menu(update,context)

    @log_errors
    def submit_price_statistic(self, update: Update, context: CallbackContext):
        print("ВЫБОР АЗС СТАТИСТИКА1")
        chat_id = update.effective_user['id']
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.effective_user['username']}
        )
        context.user_data['user_id'] = chat_id
        gas_station_id = update.callback_query.data.split('_')[-1]
        if gas_station_id== 'all':
            prices = FuelPrice.objects.filter(fuel_type=user.active_filter.target_fuel,
                                              date__gte=datetime.now() - timedelta(days=30)).order_by('date')\
                                        .extra(select={'datestr': "to_char(date, 'DD-MM')"})\
                                        .values('datestr').annotate(price=Avg('price'))
            prices = prices.extra(select={'datestr': "to_char(date, 'DD-MM')"})
            title = f'График изменения средней цены всех АЗС\n'
            print(prices.query)
        else:
            gas_station = GasStation.objects.get(id=gas_station_id)
            prices = FuelPrice.objects.filter(gas_station=gas_station_id, fuel_type=user.active_filter.target_fuel,
                                              date__gte=datetime.now() - timedelta(days=30)).order_by('date')
            prices = prices.extra(select={'datestr':"to_char(date, 'DD-MM')"})
            title = f'График изменения цен АЗС №{gas_station.number} {gas_station.address}\n'

        title+=f'Топливо {FUEL_DICT[user.active_filter.target_fuel]}\n'
        data_x = list(prices.values_list('price', flat=True))
        data_y = list(prices.values_list('datestr', flat=True))
        plt.clf()
        plt.plot(data_y,data_x)
        plt.title(title)
        plt.ylabel('Цена за 1 л.')
        plt.xlabel('Дата')
        plt.xticks(rotation=90)
        plt.grid()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        buf.seek(0)

        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=buf
        )

        self.main_menu(update,context,new=True)

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
        self.updater.dispatcher.add_handler(MessageHandler(Filters.location, self.filtered_gas_stations))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'^\d+$'), self.do_digit_command))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'\w+'), self.do_text_command))

        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.main_menu, pattern='main'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.add_filter_menu, pattern='m1_add_filter'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.tune_filters_menu, pattern='tune_filters'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.choose_filter, pattern=r'editfilter_\d+'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.submit_target_gas_station, pattern=r'targetgasstation_\d+'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.submit_price_statistic, pattern=r'pricestatistic_\w+'))

        self.updater.dispatcher.add_handler(
            CallbackQueryHandler(self.choose_active_filter, pattern='choose_active_filter'))
        self.updater.dispatcher.add_handler(
            CallbackQueryHandler(self.submit_active_filter, pattern=r'activefilter_\d+'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.submit_fuel_type, pattern=r'fueltype_\w+'))

        for property in GasStationProperties._meta.get_fields():
            self.updater.dispatcher.add_handler(
                CallbackQueryHandler(self.select_filter_property, pattern=property.name))

        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.change_filter_name, pattern='change_filter_name'))
        self.updater.dispatcher.add_handler(
            CallbackQueryHandler(self.change_filter_radius, pattern='change_filter_radius'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.change_target_fuel, pattern='change_target_fuel'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.price_statistic, pattern='price_statistic'))

        self.updater.start_polling()
        self.updater.idle()
