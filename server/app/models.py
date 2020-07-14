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

    stop_express = models.BooleanField(verbose_name='Магазин StopExpress')
    app_payment = models.BooleanField(verbose_name='Оплата через приложение')
    cafe = models.BooleanField(verbose_name='кафе')
    wc = models.BooleanField(verbose_name='туалет')
    eur_fuel_pistol = models.BooleanField(verbose_name='европистолет')
    round_the_clock = models.BooleanField(verbose_name='24 часа')
    postpayment = models.BooleanField(verbose_name='постоплата')
    atm = models.BooleanField(verbose_name='банкомат')
    wifi = models.BooleanField(verbose_name='wi - fi')
    atm = models.BooleanField(verbose_name='банкомат')
    automated = models.BooleanField(verbose_name='Автоматическая ')
    atm = models.BooleanField(verbose_name='банкомат')
    atm = models.BooleanField(verbose_name='банкомат')

    • терминал
    оплаты
    услуг;
    • автоматическая
    АЗС;
    • выносная
    ТРК;
    • прием
    карт «Нам
    По
    Пути»; о
    • плата
    топливной
    картой
    ГПН;
    • подкачка
    шин;
    • пылесос;
    • вода;
    • автоматическая
    мойка;
    • ручная
    мойка;
    • пункт
    приема
    шин
    для
    утилизации;
    • аренда
    прицепов;
    заправщик;
    • зарядка
    для
    мобильных
    устройств;
    • сеть
    партнерских
    АЗС;
    • зарядка
    для
    электромобилей.
