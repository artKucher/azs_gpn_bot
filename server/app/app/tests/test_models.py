from datetime import datetime

from django.contrib.gis.geos import Point
from django.test import TestCase

from app.models import User, Filter, GasStation, FuelPrice


class ModelsTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(external_id=1111, username="TestUser")
        filter = Filter.objects.create(user=user, name='TestFilter')
        gs = GasStation.objects.create(number=1111,location=Point(1,1), address='testaddr')
        fp = FuelPrice.objects.create(gas_station=gs,price=1)

    def test_user(self):
        user = User.objects.get(username="TestUser")
        self.assertEqual(str(user), '1111 TestUser')

    def test_filter(self):
        user = User.objects.get(username="TestUser")
        filter = Filter.objects.get(name='TestFilter', user=user)
        self.assertEqual(str(filter), 'Фильтр 1 TestFilter petrol92')

    def test_gas_station(self):
        gs = GasStation.objects.get(number=1111)
        p = Point(1,1)
        self.assertEqual(str(gs), f'АЗС №1111 testaddr {p.x} {p.y}')

    def test_fuel_price(self):
        fp = FuelPrice.objects.get(price=1)
        self.assertEqual(str(fp), f'Цена бензина petrol92 1.00 руб. {fp.date}')
