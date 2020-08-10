from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.db.models import Q, Subquery, OuterRef
from telegram import Update
from telegram.ext import CallbackContext
from app.models import User, GasStationProperties, GasStation, FuelPrice
from app.tgbot.choose_active_filter_menu import choose_active_filter
from app.tgbot.keyboards import choose_target_gas_station_keyboard
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

#show finded gas station list
@log_errors
def filtered_gas_stations(update: Update, context: CallbackContext):
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
        choose_active_filter(update, context, new=True)
        return
    point = Point(update.message.location.latitude, update.message.location.longitude)
    context.user_data['user_location'] = point
    active_filter = user.active_filter

    filtered_property = {}
    for field in GasStationProperties._meta.get_fields():
        value = getattr(active_filter, field.name)
        if value:
            filtered_property[field.name] = value

    fuel_price_sq = Subquery(FuelPrice.objects. \
                             filter(gas_station=OuterRef('id')). \
                             filter(Q(fuel_type=active_filter.target_fuel) | Q(fuel_type__isnull=True)). \
                             order_by('-date').values('price')[:1])
    search_radius = active_filter.search_radius
    gas_stations = []
    #extend search radius until find at least one gas_station
    for r in range(active_filter.search_radius, active_filter.search_radius * 10):
        gas_stations = GasStation.objects.filter(
            location__distance_lt=(point, Distance(km=r)),
            **filtered_property). \
            annotate(price=fuel_price_sq).order_by('price')
        if gas_stations.count():
            break
        search_radius = r
    message = ('Выберите АЗС' if search_radius == active_filter.search_radius
               else f'В радиусе {active_filter.search_radius} км. нет АЗС. '
                    f'Радиус поиска расширен до {search_radius} км.')
    update.message.reply_text(
        text=message,
        reply_markup=choose_target_gas_station_keyboard(gas_stations)
    )

#submit target gas station and create route
@log_errors
def submit_target_gas_station(update: Update, context: CallbackContext):
    log.info("ВЫБОР ЦЕЛЕВОЙ ЗАПРАВКИ")
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
    main_menu(update,context)