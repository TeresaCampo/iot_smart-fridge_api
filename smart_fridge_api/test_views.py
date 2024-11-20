from rest_framework.test import APITestCase
from .models import Fridge
from django.urls import reverse
from .serializers import FridgeSerializer
from rest_framework import status


class FridgeListTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('fridge_list')  
    
    def test_get_fridges(self):
        #create this obgjects in the test database
        self.fridge1 = Fridge.objects.create(fridge_id=1,address="Viale Pio la Torre 26", city="Modena", country="ITA")
        self.fridge2 = Fridge.objects.create(fridge_id=2,address="Via Teresina Bruchi 50", city="Modena", country="ITA")

        response = self.client.get(self.url)
        fridges = Fridge.objects.all()
        serializer = FridgeSerializer(fridges, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
     
    def test_post_fridges_valid_data(self):
        data={
            'fridge_id':5,
            'address':'Test',
            'city':'Testilandia',
            'country':'ITA'
        }
        response = self.client.post(self.url, data)
        fridge = Fridge.objects.get(fridge_id=data['fridge_id'])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(FridgeSerializer(fridge).data,data)

    def test_post_fridges_invalid_data1(self):
        data={
            'fridge_i':5,
            'address':'Test',
            'city':'Testilandia',
            'country':'ITA'
        }
        response = self.client.post(self.url, data)
       
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")
        self.assertFalse(Fridge.objects.filter(fridge_id=data['fridge_i']).exists())

    def test_post_fridges_invalid_data2(self):
        self.fridge1 = Fridge.objects.create(fridge_id=1,address="Viale Pio la Torre 26", city="Modena", country="ITA")
        data={
            'fridge_id':1,
            'address':'Test',
            'city':'Testilandia',
            'counry': 3
        }
        response = self.client.post(self.url, data)
        serializer=FridgeSerializer(data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")









