from django.db import models

# Create your models here.
class User(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя социальной сети',
        unique=True,
    )
    username = models.TextField(
        verbose_name='Юзернейм',
    )

    def __str__(self):
        return f'{self.external_id} {self.username}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

class GasStation(models.Model):
    number = models.PositiveIntegerField()
    gps = models.PointField()
    address = models.TextField()

    store = models.BooleanField(verbose_name='Магазин')
    stop_express = models.BooleanField(verbose_name='StopExpress')
    app_payment = models.BooleanField(verbose_name='Оплата через приложение')
    cafe = models.BooleanField(verbose_name='Кафе')
    wc = models.BooleanField(verbose_name='Туалет')
    eur_fuel_pistol = models.BooleanField(verbose_name='Европистолет')
    round_the_clock = models.BooleanField(verbose_name='24 часа')
    postpayment = models.BooleanField(verbose_name='Постоплата')
    atm = models.BooleanField(verbose_name='Банкомат')
    wifi = models.BooleanField(verbose_name='Wi-Fi')
    services_payment_terminal = models.BooleanField(verbose_name='Терминал оплаты услуг')
    automated = models.BooleanField(verbose_name='Автоматическая АЗС')
    remote_fuel_dispancer = models.BooleanField(verbose_name='Выносная  ТРК')
    support_npp_card = models.BooleanField(verbose_name='Прием карт «Нам По Пути»')
    support_gpn_card = models.BooleanField(verbose_name='Оплата топливной картой ГПН')
    tire_inflation = models.BooleanField(verbose_name='Подкачка шин')
    vacuum_cleaner = models.BooleanField(verbose_name='Пылесос')
    water = models.BooleanField(verbose_name='Вода')
    automated_car_wash = models.BooleanField(verbose_name='автоматическая мойка')
    hand_car_wash = models.BooleanField(verbose_name='Ручная мойка')
    tire_utilization = models.BooleanField(verbose_name='Пункт приема шин для утилизации')
    trailer_rental = models.BooleanField(verbose_name='Аренда прицепов')
    refueller = models.BooleanField(verbose_name='Заправщик')
    device_charger = models.BooleanField(verbose_name='Зарядка для мобильных устройств')
    partner_gas_station = models.BooleanField(verbose_name='Cеть партнерских АЗС')
    electrocar_charger = models.BooleanField(verbose_name='Зарядка для электромобилей')

    def __str__(self):
        return f'АЗС №{self.number} {self.address} {self.gps}'

    class Meta:
        verbose_name = 'АЗС'
        verbose_name_plural = 'АЗС'
