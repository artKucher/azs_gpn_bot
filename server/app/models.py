from django.db import models
from django.contrib.gis.db.models import PointField
from django.utils.timezone import now
from djmoney.models.fields import MoneyField


class Fuel:
    diesel = 'diesel'
    gdiesel = 'gdiesel'
    diesel_opti = 'gdiesel-opti'
    petrol92 = 'petrol92'
    gpetrol92 = 'gpetrol92'
    petrol92_opti = 'petrol92-opti'
    petrol95 = 'petrol95'
    gpetrol95 = 'gpetrol95'
    petrol95_opti = 'petrol95-opti'
    petrol98 = 'petrol98'
    gpetrol100 = 'gpetrol100'
    gas = 'gas'


FUEL_DICT = {
    Fuel.diesel: 'ДТ',
    Fuel.gdiesel: 'G-ДТ',
    Fuel.diesel_opti: 'ДТ Опти',
    Fuel.petrol92: '92',
    Fuel.gpetrol92: 'G-92',
    Fuel.petrol92_opti: '92 Опти',
    Fuel.petrol95: '95',
    Fuel.gpetrol95: 'G-95',
    Fuel.petrol95_opti: '95 Опти',
    Fuel.petrol98: '98',
    Fuel.gpetrol100: 'G-100',
    Fuel.gas: 'ГАЗ',
}

FUEL_CHOICES = tuple([(k, v) for k, v in FUEL_DICT.items()])


# Create your models here.
class User(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя социальной сети',
        unique=True,
    )
    username = models.TextField(
        verbose_name='Юзернейм',
    )
    active_filter = models.ForeignKey('Filter', on_delete=models.SET_NULL, null=True, related_name='active_filter_rel')
    def __str__(self):
        return f'{self.external_id} {self.username}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

class GasStationProperties(models.Model):
    store = models.BooleanField(verbose_name='Магазин', default=0)
    stop_express = models.BooleanField(verbose_name='StopExpress', default=0)
    app_payment = models.BooleanField(verbose_name='Оплата в приложении', default=0)
    cafe = models.BooleanField(verbose_name='Кафе', default=0)
    wc = models.BooleanField(verbose_name='Туалет', default=0)
    eur_fuel_pistol = models.BooleanField(verbose_name='Европистолет', default=0)
    round_the_clock = models.BooleanField(verbose_name='Круглосуточная работа', default=0)
    postpayment = models.BooleanField(verbose_name='Постоплата', default=0)
    atm = models.BooleanField(verbose_name='Банкомат', default=0)
    wifi = models.BooleanField(verbose_name='Wi-Fi', default=0)
    services_payment_terminal = models.BooleanField(verbose_name='Терминал оплаты услуг', default=0)
    automated = models.BooleanField(verbose_name='Автоматическая АЗС', default=0)
    remote_fuel_dispancer = models.BooleanField(verbose_name='Выносная ТРК', default=0)
    support_npp_card = models.BooleanField(verbose_name='Прием карт «Нам По Пути»', default=0)
    support_gpn_card = models.BooleanField(verbose_name='Оплата топливной картой ГПН', default=0)
    tire_inflation = models.BooleanField(verbose_name='Подкачка шин', default=0)
    vacuum_cleaner = models.BooleanField(verbose_name='Пылесос', default=0)
    water = models.BooleanField(verbose_name='Вода', default=0)
    automated_car_wash = models.BooleanField(verbose_name='Aвтоматическая мойка', default=0)
    hand_car_wash = models.BooleanField(verbose_name='Ручная мойка', default=0)
    tire_utilization = models.BooleanField(verbose_name='Пункт приема шин для утилизации', default=0)
    trailer_rental = models.BooleanField(verbose_name='Аренда прицепов', default=0)
    refueller = models.BooleanField(verbose_name='Заправщик', default=0)
    device_charger = models.BooleanField(verbose_name='Зарядка для мобильных устройств', default=0)
    partner_gas_station = models.BooleanField(verbose_name='Сеть партнерских АЗС', default=0)
    electrocar_charger = models.BooleanField(verbose_name='Зарядка для электромобилей', default=0)
    qr_code = models.BooleanField(verbose_name='QR код', default=0)


    class Meta:
        abstract = True

class Filter(GasStationProperties):
    search_radius = models.PositiveIntegerField(verbose_name='Радиус поиска', default=4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(blank=True, default='Без названия')
    target_fuel = models.TextField(choices=FUEL_CHOICES, default=Fuel.petrol92, max_length=15)

    class Meta:
        verbose_name = 'Фильтр АЗС'
        verbose_name_plural = 'Фильтр АЗС'

    def __str__(self):
        return f'Фильтр {self.id} {self.name} {self.target_fuel}'

class GasStation(GasStationProperties):
    number = models.PositiveIntegerField(unique=True, verbose_name='Номер АЗС')
    location = PointField()
    address = models.TextField()

    def __str__(self):
        return f'АЗС №{self.number} {self.address} {self.location.x} {self.location.y}'

    class Meta:
        verbose_name = 'АЗС'
        verbose_name_plural = 'АЗС'

class FuelPrice(models.Model):
    gas_station = models.ForeignKey(GasStation, on_delete=models.CASCADE)
    fuel_type = models.TextField(choices=FUEL_CHOICES, default=Fuel.petrol92, max_length=15)
    price = MoneyField(
        decimal_places=2,
        default=0,
        default_currency='RUB',
        max_digits=11,
    )
    date = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        return f'Цена бензина {self.fuel_type} {self.price} {self.date}'