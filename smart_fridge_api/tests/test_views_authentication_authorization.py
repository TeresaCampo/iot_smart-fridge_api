from rest_framework.test import APITestCase
from django.urls import reverse
from smart_fridge_api.models import Fridge, CustomUser
from rest_framework.authtoken.models import Token
from rest_framework import status

class SignupViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('user_signup')  
        self.fridge1 = Fridge.objects.create(fridge_id=11,address="Viale Pio la Torre 26", city="Modena", country="ITA")

    def test_singup_success(self):
        data={'email':'test@gmail.com', 'first_name': 'TestName', 'last_name':'TestSurname','fridge_id':11, 'password':'debole'}
        response=self.client.post(self.url,data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['token'])
        #returns the right data about the user
        user_returned=response.data['user']
        self.assertTrue(user_returned['email']==data['email'])
        self.assertTrue(user_returned['fridge_id']==data['fridge_id'])
        #saves the right data
        user_saved=CustomUser.objects.get(email=data['email'])
        self.assertEqual(user_saved.first_name, data['first_name'])
        self.assertEqual(user_saved.last_name, data['last_name'])
        self.assertEqual(user_saved.fridge_id, data['fridge_id'])
    
    def test_singup_not_one_field(self):
        data={'email':'test@gmail.com', 'last_name':'TestSurname','fridge_id':11, 'password':'debole'}
        response=self.client.post(self.url,data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_singup_not_existig_fridge(self):
        data={'email':'test@gmail.com', 'first_name': 'TestName', 'last_name':'TestSurname','fridge_id':10, 'password':'debole'}
        response=self.client.post(self.url,data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class LoginViewTestCase(APITestCase):
    def setUp(self):
        #create the fridge
        self.fridge1 = Fridge.objects.create(fridge_id=11,address="Viale Pio la Torre 26", city="Modena", country="ITA")
        #create the user
        self.data={'email':'test@gmail.com', 'first_name': 'TestName', 'last_name':'TestSurname','fridge_id':11, 'password':'debole'}
        url_singup = reverse('user_signup')  
        self.client.post(url_singup,self.data)
        
        self.url=reverse('user_login')
    
    def test_login_succes(self):
        login_data={'email':self.data['email'], 'password':self.data['password']}
        response=self.client.post(self.url, login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #correct token
        user = CustomUser.objects.get(email=self.data['email'])
        expected_token = Token.objects.get(user=user).key
        self.assertEqual(response.data['token'], expected_token)



        
    