# Generated by Django 3.0.8 on 2020-07-19 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_auto_20200719_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gasstation',
            name='app_payment',
            field=models.BooleanField(default=0, verbose_name='Оплата через приложение'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='atm',
            field=models.BooleanField(default=0, verbose_name='Банкомат'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='automated',
            field=models.BooleanField(default=0, verbose_name='Автоматическая АЗС'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='automated_car_wash',
            field=models.BooleanField(default=0, verbose_name='автоматическая мойка'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='cafe',
            field=models.BooleanField(default=0, verbose_name='Кафе'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='device_charger',
            field=models.BooleanField(default=0, verbose_name='Зарядка для мобильных устройств'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='electrocar_charger',
            field=models.BooleanField(default=0, verbose_name='Зарядка для электромобилей'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='eur_fuel_pistol',
            field=models.BooleanField(default=0, verbose_name='Европистолет'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='hand_car_wash',
            field=models.BooleanField(default=0, verbose_name='Ручная мойка'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='partner_gas_station',
            field=models.BooleanField(default=0, verbose_name='Cеть партнерских АЗС'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='postpayment',
            field=models.BooleanField(default=0, verbose_name='Постоплата'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='refueller',
            field=models.BooleanField(default=0, verbose_name='Заправщик'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='remote_fuel_dispancer',
            field=models.BooleanField(default=0, verbose_name='Выносная  ТРК'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='round_the_clock',
            field=models.BooleanField(default=0, verbose_name='24 часа'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='services_payment_terminal',
            field=models.BooleanField(default=0, verbose_name='Терминал оплаты услуг'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='stop_express',
            field=models.BooleanField(default=0, verbose_name='StopExpress'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='store',
            field=models.BooleanField(default=0, verbose_name='Магазин'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='support_gpn_card',
            field=models.BooleanField(default=0, verbose_name='Оплата топливной картой ГПН'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='support_npp_card',
            field=models.BooleanField(default=0, verbose_name='Прием карт «Нам По Пути»'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='tire_inflation',
            field=models.BooleanField(default=0, verbose_name='Подкачка шин'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='tire_utilization',
            field=models.BooleanField(default=0, verbose_name='Пункт приема шин для утилизации'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='trailer_rental',
            field=models.BooleanField(default=0, verbose_name='Аренда прицепов'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='vacuum_cleaner',
            field=models.BooleanField(default=0, verbose_name='Пылесос'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='water',
            field=models.BooleanField(default=0, verbose_name='Вода'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='wc',
            field=models.BooleanField(default=0, verbose_name='Туалет'),
        ),
        migrations.AlterField(
            model_name='gasstation',
            name='wifi',
            field=models.BooleanField(default=0, verbose_name='Wi-Fi'),
        ),
    ]
