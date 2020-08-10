import datetime
import re
from random import randint, uniform

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot, Update
from telegram.ext import CallbackContext, Updater, MessageHandler, Filters, CommandHandler
from telegram.utils.request import Request
from app.models import User, GasStation, FuelPrice, FUEL_DICT, GasStationProperties
from app.tgbot.azs_telegram_bot import AzsBot
import requests as req
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'fill database'

    def handle(self, *args, **options):
        # cookies = {'MyRegion': '%D0%A2%D1%8E%D0%BC%D0%B5%D0%BD%D1%81%D0%BA%D0%B0%D1%8F%20%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C',
        #            'CenterLat': '56.80244',
        #            'CenterLon': '67.39452',
        #            'MyCity': '%D0%A2%D1%8E%D0%BC%D0%B5%D0%BD%D1%81%D0%BA%D0%B0%D1%8F%20%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C',
        #            'SortIndex': '143',
        #            'cookiesession1': '6D0C4ED6RT1EI6GTD0V14ERJK14FE110'
        #            ,'PHPSESSID': 'gk8cdutrm1pl2oiuobsc5nelk6'}
        cookies = {'MyRegion': '%D0%A2%D1%8E%D0%BC%D0%B5%D0%BD%D1%81%D0%BA%D0%B0%D1%8F%20%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C',
                   'MyCity': '%D0%A2%D1%8E%D0%BC%D0%B5%D0%BD%D1%81%D0%BA%D0%B0%D1%8F%20%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C',
                   'CenterLat': '56.80244',
                   'CenterLon': '67.39452',
                   'SortIndex': '143',
                  }
        resp = req.get("https://www.gpnbonus.ru/our_azs/", cookies=cookies)
        reverse_properties_name = self.get_reverse_properties_name()
        reverse_fuel_type_name = self.get_reverse_fuel_type_name()
        soup = BeautifulSoup(resp.text, 'lxml')
        gas_stations_containers = soup.find_all('div', class_='dotted azs_container')

        for gs_container in gas_stations_containers:
            gs_number = gs_container.find('span', id=re.compile('azs_number_')).getText()[5:]
            gs_address = gs_container.find('div', class_=re.compile('DinProMedium fs18 clr6')).getText().lstrip().rstrip()
            gs_location = gs_container.find('nobr').contents[2].lstrip().rstrip().split(' ')
            gs_properties_flag = {}
            gs_properties = gs_container.find('span', class_='inline-block fs12 serviceText').getText().split(', ')
            for gs_prop in gs_properties:
                gs_properties_flag[reverse_properties_name[gs_prop]] = True
            gs, created = GasStation.objects.get_or_create(number=gs_number,
                            address=gs_address,
                            location=Point(float(gs_location[0]),
                                           float(gs_location[1])),
                            **gs_properties_flag)
            print(gs)
            fuel_type_blocks = gs_container.find_all('div',  style=re.compile('border: 0px solid; margin-right: 8px'))
            for ft_block in fuel_type_blocks:
                ft_name = ft_block.find('div', class_=re.compile('DinPro fs12 inline-block')).getText().lstrip().rstrip()
                ft_price = ft_block.find('div',
                                         class_='inline-block',
                                         style=re.compile(';color: #009CDE;font-size: 11px; display: block')).getText().split('₽')[0]
                if ft_price.isdigit():
                    FuelPrice(gas_station=gs,
                              fuel_type=ft_name,
                              price=ft_price).save()



    def get_reverse_properties_name(self):
        res = {}
        for field in GasStationProperties._meta.get_fields():
            res[field.verbose_name] = field.name
        return res

    def get_reverse_fuel_type_name(self):
        res = {}
        for key, value in FUEL_DICT.items():
            res[value] = key
        return res