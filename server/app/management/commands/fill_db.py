import datetime
from random import randint, uniform

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot, Update
from telegram.ext import CallbackContext, Updater, MessageHandler, Filters, CommandHandler
from telegram.utils.request import Request
from app.models import User, GasStation, FuelPrice, FUEL_DICT
from app.tgbot.azs_telegram_bot import AzsBot

class Command(BaseCommand):
    help = 'fill database'

    def handle(self, *args, **options):
        for i in range(0,4):
            flag = {
                'store': randint(0, 1),
                'stop_express': randint(0, 1),
                'app_payment': randint(0, 1),
                'cafe': randint(0, 1),
                'wc': randint(0, 1),
                'eur_fuel_pistol': randint(0, 1),
                'round_the_clock': randint(0, 1),
                'postpayment': randint(0, 1),
                'atm': randint(0, 1),
                'wifi': randint(0, 1),
                'services_payment_terminal': randint(0, 1),
                'automated': randint(0, 1),
                'remote_fuel_dispancer': randint(0, 1),
                'support_npp_card': randint(0, 1),
                'support_gpn_card': randint(0, 1),
                'tire_inflation': randint(0, 1),
                'vacuum_cleaner': randint(0, 1),
                'water': randint(0, 1),
                'automated_car_wash': randint(0, 1),
                'hand_car_wash': randint(0, 1),
                'tire_utilization': randint(0, 1),
                'trailer_rental': randint(0, 1),
                'refueller': randint(0, 1),
                'device_charger': randint(0, 1),
                'partner_gas_station': randint(0, 1),
                'electrocar_charger': randint(0, 1),
            }
            gs = GasStation(number=randint(1000,9999), location=Point(uniform(57.085757, 57.192989),
                                                                 uniform(65.382128, 65.795740)), **flag)
            gs.save()
            for day in range(1,30):
                for k,v in FUEL_DICT.items():
                    FuelPrice(gas_station=gs, fuel_type=k, price=randint(20+day,30+day), date=datetime.datetime(2020, 7, day, 16, 00, 00, 0)).save()