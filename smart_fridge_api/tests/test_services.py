from rest_framework.test import APITestCase
from smart_fridge_api.models import Fridge,Product
from django.urls import reverse
from rest_framework import status
from .utils import *
from datetime import datetime, timedelta, date


class MidDayUpdateTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('mid_day_update') 

        tomorrow = date.today() + timedelta(days=1)
        yesterday = date.today() - timedelta(days=1)
        today=date.today()

        self.fridge1 = Fridge.objects.create(fridge_id=1,longitude=9.186516,latitude=45.465454,toCharity_updated_today=False)
        self.product1_1= Product.objects.create(fridge=self.fridge1,barcode="1234567890123", expire_date=yesterday,name="Latte")
        self.product1_2= Product.objects.create(fridge=self.fridge1,barcode="1234567890124", expire_date=tomorrow,name="Latte")
        
        self.fridge2 = Fridge.objects.create(fridge_id=2,longitude=9.186516,latitude=45.465454,toCharity_updated_today=True)
        self.product2_1= Product.objects.create(fridge=self.fridge2,barcode="1234567890123", expire_date=today,name="Latte", toCharity=True)
        self.product2_2= Product.objects.create(fridge=self.fridge2,barcode="1234567890124", expire_date=today,name="Latte",toCharity=True)
        
        self.fridge3 = Fridge.objects.create(fridge_id=3,longitude=9.186516,latitude=45.465454,toCharity_updated_today=True)
        self.product3_1= Product.objects.create(fridge=self.fridge3,barcode="1234567890123", expire_date="2024-12-31",name="Latte")
        self.product3_2= Product.objects.create(fridge=self.fridge3,barcode="1234567890124", expire_date=tomorrow,name="Latte")

    
    def test_delete_expired_day_before(self):
        self.client.get(self.url)

        self.assertEqual(Product.objects.filter(fridge_id=self.fridge1.fridge_id).count(),1)
        self.assertEqual(Product.objects.filter(fridge_id=self.fridge3.fridge_id).count(),2)

    def test_delete_given_to_charity_products(self):
        self.client.get(self.url)

        self.assertEqual(Product.objects.filter(fridge_id=self.fridge2.fridge_id).count(),0)
    
    def test_set_false_updated_today(self):
        self.client.get(self.url)

        #reload fridge from the database        
        fridge1 = Fridge.objects.get(fridge_id=self.fridge1.fridge_id)
        fridge2 = Fridge.objects.get(fridge_id=self.fridge2.fridge_id)
        fridge3 = Fridge.objects.get(fridge_id=self.fridge3.fridge_id)

        self.assertFalse(fridge1.toCharity_updated_today)
        self.assertFalse(fridge2.toCharity_updated_today)
        self.assertFalse(fridge3.toCharity_updated_today)

class MorningUpdateTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('morning_update') 

        tomorrow = date.today() + timedelta(days=1)
        yesterday = date.today() - timedelta(days=1)
        today=date.today()

        self.fridge1 = Fridge.objects.create(fridge_id=1,longitude=9.186516,latitude=45.465454,toCharity_updated_today=False)
        self.product1_1= Product.objects.create(fridge=self.fridge1,barcode="1234567890123", expire_date=yesterday,name="Latte")
        self.product1_2= Product.objects.create(fridge=self.fridge1,barcode="1234567890124", expire_date=tomorrow,name="Latte")
        
        self.fridge2 = Fridge.objects.create(fridge_id=2,longitude=9.186516,latitude=45.465454,toCharity_updated_today=True)
        self.product2_1= Product.objects.create(fridge=self.fridge2,barcode="1234567890123", expire_date=today,name="Latte", toCharity=True)
        self.product2_2= Product.objects.create(fridge=self.fridge2,barcode="1234567890124", expire_date=today,name="Latte",toCharity=True)
        
        self.fridge3 = Fridge.objects.create(fridge_id=3,longitude=9.186516,latitude=45.465454,toCharity_updated_today=True)
        self.product3_1= Product.objects.create(fridge=self.fridge3,barcode="1234567890123", expire_date="2024-12-31",name="Latte",toCharity=True )
        self.product3_2= Product.objects.create(fridge=self.fridge3,barcode="1234567890124", expire_date=tomorrow,name="Latte")

    def test_find_fridges_which_donate(self):
        self.client.get(self.url)


