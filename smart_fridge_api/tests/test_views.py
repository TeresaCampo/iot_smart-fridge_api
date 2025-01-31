from rest_framework.test import APITestCase
from smart_fridge_api.models import Fridge,Product, Parameter
from django.urls import reverse
from smart_fridge_api.serializers import FridgeSerializer, ProductSerializer,ParameterSerializer
from rest_framework import status
from datetime import datetime, timedelta, date
import random
from django.utils import timezone
from .utils import *

#----------------------CREATE AND GET FRIDGES----------------------------------------
class FridgeListTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('fridge_list') 
        #superuser authentication
        self.client=create_super_user(self.client)

    def test_get_fridges(self):
        #create this object in the test database
        self.fridge1 = Fridge.objects.create(fridge_id=1,longitude=9.186516,latitude=45.465454)
        self.fridge2 = Fridge.objects.create(fridge_id=2,longitude=9.186516,latitude=45.465454)

        response = self.client.get(self.url)
        fridges = Fridge.objects.all()
        serializer = FridgeSerializer(fridges, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

     
    def test_update_fridges_valid_data(self):
        fridge1 = Fridge.objects.create(fridge_id=1,longitude=9.186516,latitude=45.465454)

        data={
            'fridge_id':1,
            'longitude':  9.18652,
            'latitude':45.465452
        }
        response = self.client.post(self.url, data)
        fridge = Fridge.objects.get(fridge_id=data['fridge_id'])
        if response.status_code != 200:
            print("Response Status Code:", response.status_code)
            print("Response Content:", response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data_to_check=FridgeSerializer(fridge).data
        data_to_check.pop('toCharity_updated_today')
        self.assertEqual(data_to_check,data)

    def test_post_fridges_valid_data(self):
        data={
            'fridge_id':5,
            'longitude': 9.18651,
            'latitude':45.465454
        }
        response = self.client.post(self.url, data)
        fridge = Fridge.objects.get(fridge_id=data['fridge_id'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        data_to_check=FridgeSerializer(fridge).data
        data_to_check.pop('toCharity_updated_today')
        self.assertEqual(data_to_check,data)

    def test_post_fridges_invalid_data1(self):
        data={
            'fridge_i':5,
            'longitude': 9.18651,
            'latitude':45.465454
        }
        response = self.client.post(self.url, data)
       
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Fridge.objects.filter(fridge_id=data['fridge_i']).exists())


#----------------------GET INFO ABOUT A FRIDGE----------------------------------------
class FridgeDetailTestCase(APITestCase):
    def setUp(self):
        self.fridge1 = Fridge.objects.create(fridge_id=1,longitude=9.186516,latitude=45.465454)
        self.serializer=FridgeSerializer(self.fridge1)
        #user authentication
        self.client,self.user_fridge=create_normal_user(self.client)
    
    def test_get_existing_fridge(self):
        url = reverse('fridge_detail', kwargs={'pk_fridge':self.fridge1.fridge_id})

        response=self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data,self.serializer.data)

    def test_get_not_existing_fridge(self):
        url = reverse('fridge_detail', kwargs={'pk_fridge': 2})

        response=self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

#----------------------CREATE, DELETE OR UPDATE A PRODUCT, GET PRODUCTS----------------------------------------
class FridgeProductDetailTestCase(APITestCase):
    def setUp(self):
        #fridge with 2 products with same barcode and expire date
        self.fridge1 = Fridge.objects.create(fridge_id=1,longitude=9.186516,latitude=45.465454)
        self.product1_1= Product.objects.create(fridge=self.fridge1,barcode="1234567890123", expire_date="2024-12-31",name="Latte")
        self.product1_2= Product.objects.create(fridge=self.fridge1,barcode="1234567890123", expire_date="2024-12-31",name="Cereali")
        #fridge with different products
        self.fridge2 = Fridge.objects.create(fridge_id=2,longitude=9.186516,latitude=45.465454)
        self.product2_1= Product.objects.create(fridge=self.fridge2,barcode="1234567890123", expire_date="2024-12-31",name="Latte")
        self.product1_2= Product.objects.create(fridge=self.fridge2,barcode="1234567890124", expire_date="2024-12-30",name="Cereali")
        #user authentication
        self.client,self.user_fridge=create_normal_user(self.client)

    #delete
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
        response=self.client.delete(url)

        self.assertEqual(response.status_code,status.HTTP_200_OK)
        fridge_in_question=Fridge.objects.get(fridge_id=self.fridge1.fridge_id)
        products_yet_in_fridge=Product.objects.filter(fridge=fridge_in_question.fridge_id,barcode=self.product1_1.barcode,expire_date=self.product1_1.expire_date)
        self.assertEqual(len(products_yet_in_fridge),1)
    #put
    def test_update_one_product_not_existing_fridge(self):
        url = reverse('fridge_product_detail', kwargs={'pk_fridge':3,'barcode':self.product1_1.barcode,'expire_date':self.product1_1.expire_date})
        updated_product={
            'fridge' : self.fridge1.fridge_id,
            'barcode':"updated one", 
            'expire_date':"2024-12-31",
            'name':"Updated Latte"
        }
        response=self.client.put(url, updated_product)

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
    def test_update_one_not_existing_product_existing_fridge(self):
        url = reverse('fridge_product_detail', kwargs={'pk_fridge':self.fridge2.fridge_id,'barcode':'a','expire_date':self.product2_1.expire_date})
        updated_product={
            'fridge' : self.fridge1.fridge_id,
            'barcode':"updated one", 
            'expire_date':"2024-12-31",
            'name':"Updated Latte"
        }
        response=self.client.put(url, updated_product)

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
    def test_update_one_existing_product_existing_fridge_first_of_two_identical_products(self):
        url = reverse('fridge_product_detail', kwargs={'pk_fridge':self.fridge1.fridge_id,'barcode':self.product1_1.barcode,'expire_date':self.product1_1.expire_date})
        updated_product={
            'fridge' : self.fridge1.fridge_id,
            'barcode':"updated one", 
            'expire_date':"2024-12-31",
            'name':"Updated Latte"
        }
        response=self.client.put(url,updated_product)

        self.assertEqual(response.status_code,status.HTTP_200_OK)
        #product no mor ein the database
        fridge_in_question=Fridge.objects.get(fridge_id=self.fridge1.fridge_id)
        products_yet_in_fridge=Product.objects.filter(fridge=fridge_in_question.fridge_id,barcode=self.product1_1.barcode,expire_date=self.product1_1.expire_date)
        self.assertEqual(len(products_yet_in_fridge),1)
        #check presence of updated product in the database
        product_updated_in_database=ProductSerializer(Product.objects.get(fridge=updated_product['fridge'], barcode=updated_product['barcode'],expire_date=updated_product['expire_date'])).data
        self.assertEqual(product_updated_in_database,updated_product)
    def test_update_one_existing_product_existing_fridge_changing_fridge(self):
        url = reverse('fridge_product_detail', kwargs={'pk_fridge':self.fridge1.fridge_id,'barcode':self.product1_1.barcode,'expire_date':self.product1_1.expire_date})
        updated_product={
            'fridge' : self.fridge2.fridge_id,      #different fridge_id than the one in the url
            'barcode':"updated one", 
            'expire_date':"2024-12-31",
            'name':"Updated Latte"
        }
        response=self.client.put(url,updated_product)

        self.assertEqual(response.status_code,status.HTTP_200_OK)
        #product no mor ein the database
        fridge_in_question=Fridge.objects.get(fridge_id=self.fridge1.fridge_id)
        products_yet_in_fridge=Product.objects.filter(fridge=fridge_in_question.fridge_id,barcode=self.product1_1.barcode,expire_date=self.product1_1.expire_date)
        self.assertEqual(len(products_yet_in_fridge),1)
        #check presence of updated product in the database
        product_updated_in_database=ProductSerializer(Product.objects.get(fridge=fridge_in_question.fridge_id, barcode=updated_product['barcode'],expire_date=updated_product['expire_date'])).data
        self.assertNotEqual(product_updated_in_database,updated_product)
        updated_product['fridge']=self.fridge1.fridge_id
        self.assertEqual(product_updated_in_database,updated_product)
    def test_update_one_product_not_existing_fridge(self):
        url = reverse('fridge_product_detail', kwargs={'pk_fridge':self.fridge1.fridge_id,'barcode':self.product1_1.barcode,'expire_date':self.product1_1.expire_date})
        updated_product={
            'fridge' : self.fridge1.fridge_id,
            'barcode':"updated one", 
            'expire_date':"2024-12-31",
        }
        response=self.client.put(url, updated_product)

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

class FridgeProductListTestCase(APITestCase):
    def setUp(self):
        self.fridge1 = Fridge.objects.create(fridge_id=1,longitude=9.186516,latitude=45.465454)
        self.fridge2 = Fridge.objects.create(fridge_id=2,longitude=9.186516,latitude=45.465454)
        #user authentication
        self.client,self.user_fridge=create_normal_user(self.client)

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
        self.assertFalse(Product.objects.filter(barcode='1234567890123').exists())
    
    def test_post_new_incomplete_product(self):
        url = reverse('fridge_product_list', kwargs={'pk_fridge':self.fridge1.fridge_id})
        data={'fridge' : self.fridge1.fridge_id,
              'barcode':"1234567890123", 
              'name':"Latte"}
        response=self.client.post(url, data, format='json')

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Product.objects.filter(barcode='1234567890123').exists()) 

    def test_post_new_product_associated_to_different_fridge(self):
        url = reverse('fridge_product_list', kwargs={'pk_fridge':self.fridge1.fridge_id})
        data={'fridge' : 2,
              'barcode':"1234567890123", 
              'expire_date':"2024-12-31",
              'name':"Latte"}
        response=self.client.post(url, data, format='json')

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
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

#----------------------GET EXPIRING PRODUCTS AND FLAG TOCHARITY----------------------------------------
class FridgeExpiringProductTestCase(APITestCase):
    def setUp(self):
        tomorrow = date.today() + timedelta(days=1)
        self.fridge1 = Fridge.objects.create(fridge_id=1,longitude=9.186516,latitude=45.465454,toCharity_updated_today=False)
        self.product1_1= Product.objects.create(fridge=self.fridge1,barcode="1234567890123", expire_date="2024-12-31",name="Latte")
        self.product1_2= Product.objects.create(fridge=self.fridge1,barcode="1234567890124", expire_date=tomorrow,name="Latte")
        
        self.fridge2 = Fridge.objects.create(fridge_id=2,longitude=9.186516,latitude=45.465454,toCharity_updated_today=False)
        self.product2_1= Product.objects.create(fridge=self.fridge2,barcode="1234567890123", expire_date="2024-12-31",name="Latte")
        self.product2_2= Product.objects.create(fridge=self.fridge2,barcode="1234567890124", expire_date="2024-12-31",name="Latte")
        
        self.fridge3 = Fridge.objects.create(fridge_id=3,longitude=9.186516,latitude=45.465454,toCharity_updated_today=True)
        self.product3_1= Product.objects.create(fridge=self.fridge3,barcode="1234567890123", expire_date="2024-12-31",name="Latte")
        self.product3_2= Product.objects.create(fridge=self.fridge3,barcode="1234567890124", expire_date=tomorrow,name="Latte")
        
        #user authentication
        self.client,self.user_fridge=create_normal_user(self.client)

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
        url = reverse('fridge_expiring_product', kwargs={'pk_fridge': 4})
        response=self.client.get(url)

        self.assertTrue(response.status_code,status.HTTP_404_NOT_FOUND)
    def test_already_checked_today(self):
        url = reverse('fridge_expiring_product', kwargs={'pk_fridge': self.fridge3.fridge_id})
        response=self.client.get(url)

        self.assertTrue(response.status_code,status.HTTP_304_NOT_MODIFIED)

class FridgeExpiringProductsDonate(APITestCase):
    def setUp(self):
        self.tomorrow = date.today() + timedelta(days=1)
        self.fridge1 = Fridge.objects.create(fridge_id=1,longitude=9.186516,latitude=45.465454,toCharity_updated_today=False)
        self.product1_1= Product.objects.create(fridge=self.fridge1,barcode="1234567890123", expire_date="2024-12-31",name="Latte")
        self.product1_2= Product.objects.create(fridge=self.fridge1,barcode="1234567890124", expire_date=self.tomorrow,name="Latte", toCharity=False)
        
        #user authentication
        self.client,self.user_fridge=create_normal_user(self.client)
    
    def test_flag_to_charity(self):
        url = reverse('fridge_expiring_product', kwargs={'pk_fridge': 1})
        response=self.client.post(url, data={'barcode':"1234567890124"})

        products1_2_updated=Product.objects.get(fridge=self.fridge1, barcode="1234567890124", expire_date=self.tomorrow)
        self.assertTrue(products1_2_updated.toCharity)
  

#----------------------GET TEMP/HUM PARAMETERS----------------------------------------
class FridgeParameterTestCase(APITestCase):
    def setUp(self):
        self.fridge = Fridge.objects.create(fridge_id=1,longitude=9.186516,latitude=45.465454)
        base_date = timezone.now()  

        for i in range(8):
            Parameter.objects.create(
                fridge=self.fridge,
                humidity=random.uniform(30.0, 70.0),
                temperature=random.uniform(-10.0, 10.0), 
                sampling_date=base_date - timedelta(days=i)  
            )
        #user authentication
        self.client,self.user_fridge=create_normal_user(self.client)

    #get
    def test_get_first_20_products_not_existing_fridge(self):
        url = reverse('fridge_parameter', kwargs={'pk_fridge': 3})
        response=self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_first_20_products(self):
        url = reverse('fridge_parameter', kwargs={'pk_fridge': self.fridge.fridge_id})
        response=self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8)
        self.assertTrue(response.data[0]['sampling_date']<response.data[1]['sampling_date'])
    #post
    def test_post_not_existing_fridge(self):
        url = reverse('fridge_parameter', kwargs={'pk_fridge': 3})
        new_parameters_set={
            'fridge':self.fridge,
            'humidity':random.uniform(30.0, 70.0),
            'temperature':random.uniform(-10.0, 10.0), 
            'sampling_date':timezone.now()
        }
        response=self.client.post(url, new_parameters_set)

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
    
    def test_post_new_valid_parameters(self):
        url = reverse('fridge_parameter', kwargs={'pk_fridge': self.fridge.fridge_id})
        new_parameters_set={
            'fridge':self.fridge.fridge_id,
            'humidity':random.uniform(30.0, 70.0),
            'temperature':random.uniform(-10.0, 10.0), 
            'sampling_date':'2024-12-12T21:56'
        }
        response=self.client.post(url, new_parameters_set)

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        product_just_created=ParameterSerializer(Parameter.objects.get(fridge=self.fridge.fridge_id,sampling_date=new_parameters_set['sampling_date'])).data
        self.assertEqual( new_parameters_set,product_just_created)

    def test_post_new_valid_parameters_not_temperature(self):
        url = reverse('fridge_parameter', kwargs={'pk_fridge': self.fridge.fridge_id})
        new_parameters_set={
            'fridge':self.fridge.fridge_id,
            'humidity':random.uniform(30.0, 70.0),
            'sampling_date':'2024-12-12T21:56'
        }
        response=self.client.post(url, new_parameters_set)

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        product_just_created=ParameterSerializer(Parameter.objects.get(fridge=self.fridge.fridge_id,sampling_date=new_parameters_set['sampling_date'])).data
        new_parameters_set['temperature']=None
        self.assertEqual( new_parameters_set,product_just_created)
    
    def test_post_new_valid_parameters_not_humidity(self):
        url = reverse('fridge_parameter', kwargs={'pk_fridge': self.fridge.fridge_id})
        new_parameters_set={
            'fridge':self.fridge.fridge_id,
            'sampling_date':'2024-12-12T21:56'
        }
        response=self.client.post(url, new_parameters_set)

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        product_just_created=ParameterSerializer(Parameter.objects.get(fridge=self.fridge.fridge_id,sampling_date=new_parameters_set['sampling_date'])).data
        new_parameters_set['humidity']=None
        new_parameters_set['temperature']=None
        self.assertEqual( new_parameters_set,product_just_created)
    def test_post_no_body(self):
        url = reverse('fridge_parameter', kwargs={'pk_fridge': self.fridge.fridge_id})
        new_parameters_set={
            'fridge':self.fridge.fridge_id,
            'sampling_date':'2024-12-12T21:56'
        }
        response=self.client.post(url)

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)





      
   










