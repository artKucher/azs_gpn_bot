################################# Keyboards #########################################
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from app.models import GasStationProperties, FUEL_DICT
from backend.settings import FILTERS_COUNT


def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Настроить фильтры', callback_data='tune_filters')],
                [InlineKeyboardButton('Выбрать активный фильтр', callback_data='choose_active_filter')],
                [InlineKeyboardButton('Динамика цены', callback_data='price_statistic')]]
    return InlineKeyboardMarkup(keyboard)


def tune_filters_keyboard(filters):
    keyboard = []
    for filter in filters:
        keyboard.append([InlineKeyboardButton((filter.name if filter.name else 'Фильтр'),
                                              callback_data='editfilter_' + str(filter.id))])
    if filters.count() < FILTERS_COUNT:
        keyboard.append([InlineKeyboardButton('Создать фильтр', callback_data='m1_add_filter'),
                         InlineKeyboardButton('Главное меню', callback_data='main')])
    else:
        keyboard.append([InlineKeyboardButton('Главное меню', callback_data='main')])

    return InlineKeyboardMarkup(keyboard)


def choose_active_filter_keyboard(filters):
    keyboard = []
    for filter in filters:
        keyboard.append([InlineKeyboardButton((filter.name if filter.name else 'Фильтр'),
                                              callback_data='activefilter_' + str(filter.id))])
    keyboard.append([InlineKeyboardButton('Главное меню', callback_data='main')])
    return InlineKeyboardMarkup(keyboard)


def price_statistic_keyboard(gas_stations):
    keyboard = []
    keyboard.append([InlineKeyboardButton('Среднее по всем АЗС', callback_data='pricestatistic_all')])
    for gs in gas_stations:
        keyboard.append([InlineKeyboardButton(f'#{gs.number} {gs.address}',
                                              callback_data='pricestatistic_' + str(gs.id))])
    keyboard.append([InlineKeyboardButton('Главное меню', callback_data='main')])
    return InlineKeyboardMarkup(keyboard)


def choose_fuel_type_keyboard(fuel_types):
    keyboard = []
    for ft1, ft2, ft3, ft4 in zip(fuel_types[0::4], fuel_types[1::4], fuel_types[2::4], fuel_types[3::4]):
        keyboard.append([
            InlineKeyboardButton(ft1[1], callback_data='fueltype_' + str(ft1[0])),
            InlineKeyboardButton(ft2[1], callback_data='fueltype_' + str(ft2[0])),
            InlineKeyboardButton(ft3[1], callback_data='fueltype_' + str(ft3[0])),
            InlineKeyboardButton(ft4[1], callback_data='fueltype_' + str(ft4[0]))
        ])
    keyboard.append([InlineKeyboardButton('Главное меню', callback_data='main')])
    return InlineKeyboardMarkup(keyboard)


def edit_filter_keyboard(context):
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
    keyboard.append([InlineKeyboardButton(f"Изменить название: \"{getattr(filter, 'name')}\"", callback_data='change_filter_name')])
    keyboard.append(
        [InlineKeyboardButton(f"Изменить радиус поиска: {getattr(filter, 'search_radius')} км.", callback_data='change_filter_radius')])
    keyboard.append([InlineKeyboardButton(f"Изменить топливо: {FUEL_DICT[getattr(filter, 'target_fuel')]}",
                                          callback_data='change_target_fuel')])
    keyboard.append([InlineKeyboardButton('Главное меню', callback_data='main')])

    return InlineKeyboardMarkup(keyboard)


def choose_target_gas_station_keyboard(gas_stations):
    keyboard = []
    for gs in gas_stations:
        keyboard.append([InlineKeyboardButton((f'{(str(gs.price) + " ₽" if gs.price else "")} {gs.address}'),
                                              callback_data='targetgasstation_' + str(gs.id))])
    keyboard.append([InlineKeyboardButton('Главное меню', callback_data='main')])
    return InlineKeyboardMarkup(keyboard)