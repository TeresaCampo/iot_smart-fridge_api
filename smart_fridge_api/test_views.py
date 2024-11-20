from rest_framework.test import APITestCase
from .models import Fridge,Product
from django.urls import reverse
from .serializers import FridgeSerializer, ProductSerializer
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

    def test_post_fridges_already_existing(self):
        self.fridge1 = Fridge.objects.create(fridge_id=1,address="Viale Pio la Torre 26", city="Modena", country="ITA")
        data={
            'fridge_id':1,
            'address':'Test',
            'city':'Testilandia',
            'country': 'ITA'
        }
        response = self.client.post(self.url, data)
        serializer=FridgeSerializer(data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")


class FridgeDetailTestCase(APITestCase):
    def setUp(self):
        self.fridge1 = Fridge.objects.create(fridge_id=1,address="Viale Pio la Torre 26", city="Modena", country="ITA")
        self.serializer=FridgeSerializer(self.fridge1)
    
    def test_get_existing_fridge(self):
        url = reverse('fridge_detail', kwargs={'pk_fridge':self.fridge1.fridge_id})

        response=self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data,self.serializer.data)

    def test_get_not_existing_fridge(self):
        url = reverse('fridge_detail', kwargs={'pk_fridge': 2})

        response=self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

class FridgeProductTestCase(APITestCase):
    def setUp(self):
        self.fridge1 = Fridge.objects.create(fridge_id=1,address="Viale Pio la Torre 26", city="Modena", country="ITA")
        self.fridge2 = Fridge.objects.create(fridge_id=2,address="Via Teresina Bruchi 50", city="Modena", country="ITA")
        #self.product1= Product.objects.create(fridge=self.fridge1,barcode="1234567890123", expire_date="2024-12-31",name="Latte")

    def test_post_new_valid_product(self):
        url = reverse('fridge_product', kwargs={'pk_fridge':self.fridge1.fridge_id})
        data={'fridge' : self.fridge1.fridge_id,
              'barcode':"1234567890123", 
              'expire_date':"2024-12-31",
              'name':"Latte"}
        response=self.client.post(url, data, format='json')
        product=Product.objects.get(barcode="1234567890123")

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(data,ProductSerializer(product).data)        

    def test_post_new_product_non_existing_fridge(self):
        url=reverse('fridge_product',kwargs={'pk_fridge':3})
        data={'fridge' : 3,
              'barcode':"1234567890123", 
              'expire_date':"2024-12-31",
              'name':"Latte"}
        
        response=self.client.post(url,data)

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
        self.assertFalse(Product.objects.filter(barcode='1234567890123').exists())

    def test_post_new_invalid_product(self):
        url = reverse('fridge_product', kwargs={'pk_fridge':self.fridge1.fridge_id})
        data={'fridge' : self.fridge1.fridge_id,
              'barcde':"1234567890123", 
              'expire_date':"2024-12-31",
              'name':"Latte"}
        response=self.client.post(url, data)

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'],'error')
        self.assertFalse(Product.objects.filter(barcode='1234567890123').exists())
    
    def test_post_new_incomplete_product(self):
        url = reverse('fridge_product', kwargs={'pk_fridge':self.fridge1.fridge_id})
        data={'fridge' : self.fridge1.fridge_id,
              'barcode':"1234567890123", 
              'name':"Latte"}
        response=self.client.post(url, data, format='json')

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'],'error')
        self.assertFalse(Product.objects.filter(barcode='1234567890123').exists()) 

    def test_post_new_product_associated_to_different_fridge(self):
        url = reverse('fridge_product', kwargs={'pk_fridge':self.fridge1.fridge_id})
        data={'fridge' : 2,
              'barcode':"1234567890123", 
              'expire_date':"2024-12-31",
              'name':"Latte"}
        response=self.client.post(url, data, format='json')

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'],'success')
        self.assertEqual(Product.objects.get(barcode='1234567890123').fridge, self.fridge1)
    
    def tet_get_all_products(self):
        self.product1 = Product.objects.create(fridge=self.fridge1,barcode="aaaa000193", expire_date="2024-12-31", name="latte")
        self.product1 = Product.objects.create(fridge=self.fridge1,barcode="aaaa1111193", expire_date="2022-12-31", name="uova")
        self.product1 = Product.objects.create(fridge=self.fridge2,barcode="aaaa1111193", expire_date="2022-12-31", name="uova")

        url = reverse('fridge_product', kwargs={'pk_fridge':self.fridge1.fridge_id})
        request=self.client.get(url)
        
        self.assertEqual(request.data, Product.objects.get(fridge=self.fridge1))















