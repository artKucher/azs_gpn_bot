import operator

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.db.models import Prefetch, Min, Max, F, Q, Subquery, OuterRef, Count
from telegram import Bot, Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from telegram.utils.request import Request
from app.models import User, Filter, GasStationProperties, GasStation, FUEL_DICT, FUEL_CHOICES, FuelPrice
from backend.settings import FILTERS_COUNT


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
    def do_start(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.message.from_user.username}
        )
        context.user_data['user_id'] = chat_id
        update.message.reply_text(
            text=f"Ok let's get it",
            reply_markup=self.main_menu_keyboard()
        )

    @log_errors
    def filtered_gas_stations(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.message.from_user.username}
        )
        context.user_data['user_id'] = chat_id
        if not user.active_filter:
            filters = Filter.objects.filter(user=user)[:FILTERS_COUNT]
            update.message.reply_text(
                text=f"Выберете активный фильтр",
                reply_markup=self.choose_active_filter_keyboard(filters)
            )
            return
        print(GasStation.objects.all()[0].location)
        point = Point(update.message.location.latitude, update.message.location.longitude)
        context.user_data['user_location'] = point
        active_filter = user.active_filter

        filtered_property = {}
        for field in GasStationProperties._meta.get_fields():
            value = getattr(active_filter, field.name)
            if value:
                filtered_property[field.name] = value

        # gas_stations = GasStation.objects.filter(location__distance_lt=(point, Distance(km=active_filter.search_radius)),
        #                                         **filtered_property).\
        #    filter(fuelprice__fuel_type=active_filter.target_fuel)
        # FuelPrice.objects.filter(gas_stations=gas_stations, fuel_type=active_filter.target_fuel)
        lastest_prices_pks = FuelPrice.objects.filter(fuel_type=active_filter.target_fuel).\
            order_by('gas_station','-date').distinct('gas_station').values_list('id', flat=True)

        # gas_stations = GasStation.objects.filter(
        #     location__distance_lt=(point, Distance(km=active_filter.search_radius)),
        #     **filtered_property). \
        #     prefetch_related(Prefetch('fuelprice_set',
        #                               queryset=FuelPrice.objects.filter(id__in=lastest_prices_pks),
        #                               to_attr='fuelprices')).values_list(flat=True)\

                                    #.annotate(price=Min('fuelprice__price'))
                                     #queryset=FuelPrice.objects.filter(fuel_type=active_filter.target_fuel).order_by('-date').latest('id'))) \

                                    #.order_by('id', '-fuelprice__date').distinct('id')

        # gas_stations = GasStation.objects.filter(
        #     location__distance_lt=(point, Distance(km=active_filter.search_radius)),
        #     **filtered_property).\
        #     annotate(
        #             pd=F('fuelprice__date'),
        #             price=F('fuelprice__price'),
        #             ft=F('fuelprice__fuel_type')
        #             ).\
        #     filter(Q(ft=active_filter.target_fuel) | Q(ft__isnull=True))\
        #     .order_by('id', '-pd').distinct('id')
        #gas_stations = sorted(gas_stations, key=operator.attrgetter('price'), reverse=True)

        # gas_stations = GasStation.objects.filter(
        #     location__distance_lt=(point, Distance(km=active_filter.search_radius)),
        #     **filtered_property). \
        #     annotate(
        #     pd=F('fuelprice__date'),
        #     price=F('fuelprice__price'),
        #     ft=F('fuelprice__fuel_type')
        # ). \
        #     filter(Q(ft=active_filter.target_fuel) | Q(ft__isnull=True))\
        #     .order_by('id', '-pd').distinct('id')
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
            reply_markup=self.choose_target_gas_station_keyboard(gas_stations)
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
                    reply_markup=self.edit_filter_keyboard(context)
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
                    reply_markup=self.edit_filter_keyboard(context)
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
    def main_menu(self, update: Update, context: CallbackContext):
        print('MAIN MENU')
        context.user_data['editable_filter'] = None

        chat_id = update.effective_user['id']
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.effective_user['username']}
        )
        context.user_data['user_id'] = chat_id

        query = update.callback_query
        query.answer()
        active_filter = user.active_filter
        query.edit_message_text(
            text=f'Главное меню. Aктивный фильтр {": " + active_filter.name if active_filter else "не выбран"}',
            reply_markup=self.main_menu_keyboard())

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
            reply_markup=self.tune_filters_keyboard(filters))

    @log_errors
    def add_filter_menu(self, update: Update, context: CallbackContext):
        print('ДОБАВИТЬ ФИЛЬТР')
        chat_id = update.effective_user['id']
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.effective_user['username']}
        )
        new_filter = Filter(user=user)
        new_filter.save()
        context.user_data['editable_filter'] = new_filter
        self.edit_filter_menu(update, context)

    @log_errors
    def edit_filter_menu(self, update: Update, context: CallbackContext):
        print('ОТРЕДАКТИРОВАТЬ ФИЛЬТР')
        print(context)
        filter = context.user_data['editable_filter']
        chat_id = update.effective_user['id']
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.effective_user['username']}
        )

        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text=f'{filter.name} редактирование',
            reply_markup=self.edit_filter_keyboard(context)
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
            text=f'Редактирование фильтра {filter.name}',
            reply_markup=self.edit_filter_keyboard(context)
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
    def choose_active_filter(self, update: Update, context: CallbackContext):
        print('ВЫБОР АКТИВНОГО ФИЛЬТРА')
        chat_id = update.effective_user['id']
        user, created = User.objects.get_or_create(
            external_id=chat_id,
            defaults={'username': update.effective_user['username']}
        )
        filters = Filter.objects.filter(user=user)[:FILTERS_COUNT]
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text='Выберите активный фильтр:',
            reply_markup=self.choose_active_filter_keyboard(filters))

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
            reply_markup=self.choose_fuel_type_keyboard(fuel_types)
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

    ################################# Keyboards #########################################
    def main_menu_keyboard(self):
        keyboard = [[InlineKeyboardButton('Настроить фильтры', callback_data='tune_filters')],
                    [InlineKeyboardButton('Выбрать активный фильтр', callback_data='choose_active_filter')],
                    [InlineKeyboardButton('Option 3', callback_data='m3')]]
        return InlineKeyboardMarkup(keyboard)

    def tune_filters_keyboard(self, filters):
        keyboard = []
        for filter in filters:
            keyboard.append([InlineKeyboardButton((filter.name if filter.name else 'Фильтр'),
                                                  callback_data='editfilter_' + str(filter.id))])
        if filters.count() < FILTERS_COUNT:
            keyboard.append([InlineKeyboardButton('Add filter', callback_data='m1_add_filter'),
                             InlineKeyboardButton('Main menu', callback_data='main')])
        else:
            keyboard.append([InlineKeyboardButton('Main menu', callback_data='main')])

        return InlineKeyboardMarkup(keyboard)

    def choose_active_filter_keyboard(self, filters):
        keyboard = []
        for filter in filters:
            keyboard.append([InlineKeyboardButton((filter.name if filter.name else 'Фильтр'),
                                                  callback_data='activefilter_' + str(filter.id))])
        keyboard.append([InlineKeyboardButton('Main menu', callback_data='main')])
        return InlineKeyboardMarkup(keyboard)

    def choose_fuel_type_keyboard(self, fuel_types):
        keyboard = []
        for ft1, ft2, ft3, ft4 in zip(fuel_types[0::4], fuel_types[1::4], fuel_types[2::4], fuel_types[3::4]):
            keyboard.append([
                InlineKeyboardButton(ft1[1], callback_data='fueltype_' + str(ft1[0])),
                InlineKeyboardButton(ft2[1], callback_data='fueltype_' + str(ft2[0])),
                InlineKeyboardButton(ft3[1], callback_data='fueltype_' + str(ft3[0])),
                InlineKeyboardButton(ft4[1], callback_data='fueltype_' + str(ft4[0]))
            ])
        keyboard.append([InlineKeyboardButton('Main menu', callback_data='main')])
        return InlineKeyboardMarkup(keyboard)

    def edit_filter_keyboard(self, context):
        filter = context.user_data['editable_filter']
        keyboard = []
        fields = GasStationProperties._meta.get_fields()
        for field1, field2, field3 in zip(fields[0::3], fields[1::3], fields[2::3]):
            name1 = ('✅ ' if getattr(filter, field1.name) else '') + field1.verbose_name
            name2 = ('✅ ' if getattr(filter, field2.name) else '') + field2.verbose_name
            name3 = ('✅ ' if getattr(filter, field3.name) else '') + field3.verbose_name
            keyboard.append([
                InlineKeyboardButton(name1, callback_data=field1.name),
                InlineKeyboardButton(name2, callback_data=field2.name),
                InlineKeyboardButton(name3, callback_data=field3.name)
            ])
        keyboard.append([InlineKeyboardButton(f"'{getattr(filter, 'name')}'", callback_data='change_filter_name')])
        keyboard.append(
            [InlineKeyboardButton(f"{getattr(filter, 'search_radius')} км.", callback_data='change_filter_radius')])
        keyboard.append([InlineKeyboardButton(f"Топливо: {FUEL_DICT[getattr(filter, 'target_fuel')]}",
                                              callback_data='change_target_fuel')])
        keyboard.append([InlineKeyboardButton('Главное меню', callback_data='main')])

        return InlineKeyboardMarkup(keyboard)

    def choose_target_gas_station_keyboard(self, gas_stations):
        keyboard = []
        for gs in gas_stations:
            keyboard.append([InlineKeyboardButton((f'{(str(gs.price)+" ₽" if gs.price else "")} {gs.address}'),
                                                  callback_data='targetgasstation_' + str(gs.id))])
        keyboard.append([InlineKeyboardButton('Main menu', callback_data='main')])
        return InlineKeyboardMarkup(keyboard)

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
        self.updater.dispatcher.add_handler(MessageHandler(Filters.location, self.filtered_gas_stations))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'^\d+$'), self.do_digit_command))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'\w+'), self.do_text_command))

        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.main_menu, pattern='main'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.add_filter_menu, pattern='m1_add_filter'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.tune_filters_menu, pattern='tune_filters'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.choose_filter, pattern=r'editfilter_\d+'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.submit_target_gas_station, pattern=r'targetgasstation_\d+'))

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

        self.updater.start_polling()
        self.updater.idle()
