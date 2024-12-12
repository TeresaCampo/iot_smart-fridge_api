from rest_framework.test import APITestCase
from .models import Fridge,Product
from django.urls import reverse
from .serializers import FridgeSerializer, ProductSerializer
from rest_framework import status
from datetime import date, timedelta


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

class FridgeProductListTestCase(APITestCase):
    def setUp(self):
        self.fridge1 = Fridge.objects.create(fridge_id=1,address="Viale Pio la Torre 26", city="Modena", country="ITA")
        self.fridge2 = Fridge.objects.create(fridge_id=2,address="Via Teresina Bruchi 50", city="Modena", country="ITA")
        #self.product1= Product.objects.create(fridge=self.fridge1,barcode="1234567890123", expire_date="2024-12-31",name="Latte")

    def test_post_new_valid_product(self):
        url = reverse('fridge_product_list', kwargs={'pk_fridge':self.fridge1.fridge_id})
        data={'fridge' : self.fridge1.fridge_id,
              'barcode':"1234567890123", 
              'expire_date':"2024-12-31",
              'name':"Latte"}
        response=self.client.post(url, data, format='json')
        product=Product.objects.get(barcode="1234567890123")

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(data,ProductSerializer(product).data)        

    def test_post_new_product_non_existing_fridge(self):
        url=reverse('fridge_product_list',kwargs={'pk_fridge':3})
        data={'fridge' : 3,
              'barcode':"1234567890123", 
              'expire_date':"2024-12-31",
              'name':"Latte"}
        
        response=self.client.post(url,data)

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
        self.assertFalse(Product.objects.filter(barcode='1234567890123').exists())

    def test_post_new_invalid_product(self):
        url = reverse('fridge_product_list', kwargs={'pk_fridge':self.fridge1.fridge_id})
        data={'fridge' : self.fridge1.fridge_id,
              'barcde':"1234567890123", 
              'expire_date':"2024-12-31",
              'name':"Latte"}
        response=self.client.post(url, data)

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'],'error')
        self.assertFalse(Product.objects.filter(barcode='1234567890123').exists())
    
    def test_post_new_incomplete_product(self):
        url = reverse('fridge_product_list', kwargs={'pk_fridge':self.fridge1.fridge_id})
        data={'fridge' : self.fridge1.fridge_id,
              'barcode':"1234567890123", 
              'name':"Latte"}
        response=self.client.post(url, data, format='json')

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'],'error')
        self.assertFalse(Product.objects.filter(barcode='1234567890123').exists()) 

    def test_post_new_product_associated_to_different_fridge(self):
        url = reverse('fridge_product_list', kwargs={'pk_fridge':self.fridge1.fridge_id})
        data={'fridge' : 2,
              'barcode':"1234567890123", 
              'expire_date':"2024-12-31",
              'name':"Latte"}
        response=self.client.post(url, data, format='json')

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'],'success')
        self.assertEqual(Product.objects.get(barcode='1234567890123').fridge, self.fridge1)
    
    def test_get_all_products(self):
        self.product1 = Product.objects.create(fridge=self.fridge1,barcode="aaaa000193", expire_date="2024-12-31", name="latte")
        self.product2 = Product.objects.create(fridge=self.fridge1,barcode="aaaa1111193", expire_date="2022-12-31", name="uova")
        self.product3 = Product.objects.create(fridge=self.fridge2,barcode="aaaa1111193", expire_date="2022-12-31", name="uova again")

        url = reverse('fridge_product_list', kwargs={'pk_fridge':self.fridge1.fridge_id})
        response=self.client.get(url)
        expected_products=Product.objects.filter(fridge=self.fridge1)
        expected_products=ProductSerializer(expected_products,many=True).data
        self.assertEqual(len(response.data),len(expected_products))
        self.assertEqual(response.data, expected_products)

class FridgeExpiringProductTestCase(APITestCase):
    def setUp(self):
        tomorrow = date.today() + timedelta(days=1)
        self.fridge1 = Fridge.objects.create(fridge_id=1,address="Viale Pio la Torre 26", city="Modena", country="ITA")
        self.product1_1= Product.objects.create(fridge=self.fridge1,barcode="1234567890123", expire_date="2024-12-31",name="Latte")
        self.product1_2= Product.objects.create(fridge=self.fridge1,barcode="1234567890124", expire_date=tomorrow,name="Latte")
        
        self.fridge2 = Fridge.objects.create(fridge_id=2,address="Via Teresina Bruchi 50", city="Modena", country="ITA")
        self.product2_1= Product.objects.create(fridge=self.fridge1,barcode="1234567890123", expire_date="2024-12-31",name="Latte")
        self.product2_2= Product.objects.create(fridge=self.fridge1,barcode="1234567890124", expire_date="2024-12-31",name="Latte")

    def test_get_one_expiring_product(self):
        url = reverse('fridge_expiring_product', kwargs={'pk_fridge': self.fridge1.fridge_id})
        response=self.client.get(url)
        
        self.assertEqual(response.status_code,status.HTTP_200_OK)   
        expected_products = ProductSerializer([self.product1_2], many=True).data
        self.assertEqual(response.data, expected_products)
    def test_no_expiring_products(self):
        url = reverse('fridge_expiring_product', kwargs={'pk_fridge': self.fridge2.fridge_id})
        response=self.client.get(url)

        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),0)
    def test_not_existing_fridge(self):
        url = reverse('fridge_expiring_product', kwargs={'pk_fridge': 3})
        response=self.client.get(url)

        self.assertTrue(response.status_code,status.HTTP_404_NOT_FOUND)

class FridgeProductDetailTestCase(APITestCase):
    def setUp(self):
        #fridge with 2 products with same barcode and expire date
        self.fridge1 = Fridge.objects.create(fridge_id=1,address="Viale Pio la Torre 26", city="Modena", country="ITA")
        self.product1_1= Product.objects.create(fridge=self.fridge1,barcode="1234567890123", expire_date="2024-12-31",name="Latte")
        self.product1_2= Product.objects.create(fridge=self.fridge1,barcode="1234567890123", expire_date="2024-12-31",name="Cereali")
        #fridge with different products
        self.fridge2 = Fridge.objects.create(fridge_id=2,address="Via Teresina Bruchi 50", city="Modena", country="ITA")
        self.product2_1= Product.objects.create(fridge=self.fridge2,barcode="1234567890123", expire_date="2024-12-31",name="Latte")
        self.product1_2= Product.objects.create(fridge=self.fridge2,barcode="1234567890124", expire_date="2024-12-30",name="Cereali")
    
    def test_delete_one_product_not_existing_fridge(self):
        url = reverse('fridge_product_detail', kwargs={'pk_fridge':3,'barcode':self.product1_1.barcode,'expire_date':self.product1_1.expire_date})
        response=self.client.delete(url)

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

    def test_delete_one_not_existing_product_existing_fridge(self):
        url = reverse('fridge_product_detail', kwargs={'pk_fridge':self.fridge2.fridge_id,'barcode':'a','expire_date':self.product2_1.expire_date})
        response=self.client.delete(url)

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

    def test_delete_one_existing_product_existing_fridge_first_of_two_identical_products(self):
        url = reverse('fridge_product_detail', kwargs={'pk_fridge':self.fridge1.fridge_id,'barcode':self.product1_1.barcode,'expire_date':self.product1_1.expire_date})
        fridge_in_question=Fridge.objects.get(fridge_id=self.fridge1.fridge_id)
        print(Product.objects.filter(fridge=fridge_in_question.fridge_id,barcode=self.product1_1.barcode,expire_date=self.product1_1.expire_date))
        response=self.client.delete(url)

        self.assertEqual(response.status_code,status.HTTP_200_OK)

        products_yet_in_fridge=Product.objects.filter(fridge=fridge_in_question.fridge_id,barcode=self.product1_1.barcode,expire_date=self.product1_1.expire_date)
        print(products_yet_in_fridge)
        self.assertEqual(len(products_yet_in_fridge),1)











      
   










