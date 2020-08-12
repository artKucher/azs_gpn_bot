import io
from datetime import timedelta

from django.db.models import Avg
from django.utils.datetime_safe import datetime
from telegram import Update
from telegram.ext import CallbackContext
from app.models import User,GasStation, FUEL_DICT, FuelPrice
from app.tgbot.keyboards import price_statistic_keyboard
import matplotlib.pyplot as plt
from app.tgbot.main_menu import main_menu
from app.tgbot.choose_active_filter_menu import choose_active_filter
import logging as log

log.basicConfig(filename="sample.log", level=log.INFO)

def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'ОШИБКА {e}'
            print(error_message)
            raise e

    return inner

#show gas stations list
@log_errors
def price_statistic(update: Update, context: CallbackContext):
    log.info('ВЫБОР АЗС СТАТИСТИКА')
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
        choose_active_filter(update, context, new=True)
        return
    gas_stations = GasStation.objects.all()
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Выберите станцию для просмотра динамики цены:',
        reply_markup=price_statistic_keyboard(gas_stations))

#create price plot
@log_errors
def submit_price_statistic(update: Update, context: CallbackContext):
    log.info("ВЫБОР АЗС СТАТИСТИКА1")
    chat_id = update.effective_user['id']
    user, created = User.objects.get_or_create(
        external_id=chat_id,
        defaults={'username': update.effective_user['username']}
    )
    context.user_data['user_id'] = chat_id
    gas_station_id = update.callback_query.data.split('_')[-1]
    if gas_station_id == 'all':
        prices = FuelPrice.objects.filter(fuel_type=user.active_filter.target_fuel,
                                          date__gte=datetime.now() - timedelta(days=30)).order_by('datestr') \
            .extra(select={'datestr': "to_char(date, 'DD-MM')"}) \
            .values('datestr').annotate(price=Avg('price'))
        prices = prices.extra(select={'datestr': "to_char(date, 'DD-MM')"})
        title = f'График изменения средней цены всех АЗС\n'
        print(prices.query)
    else:
        gas_station = GasStation.objects.get(id=gas_station_id)
        prices = FuelPrice.objects.filter(gas_station=gas_station_id, fuel_type=user.active_filter.target_fuel,
                                          date__gte=datetime.now() - timedelta(days=30)).order_by('date')
        prices = prices.extra(select={'datestr': "to_char(date, 'DD-MM')"})
        title = f'График изменения цен АЗС №{gas_station.number} {gas_station.address}\n'

    title += f'Топливо {FUEL_DICT[user.active_filter.target_fuel]}\n'
    data_x = list(prices.values_list('price', flat=True))
    data_y = list(prices.values_list('datestr', flat=True))
    plt.clf()
    plt.plot(data_y, data_x)
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

    main_menu(update, context, new=True)