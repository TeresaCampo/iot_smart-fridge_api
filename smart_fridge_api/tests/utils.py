from rest_framework.test import APIClient
from smart_fridge_api.models import Fridge, CustomUser
from django.urls import reverse
from rest_framework.authtoken.models import Token

def create_normal_user(client: APIClient):
    #create the fridge
    user_fridge = Fridge.objects.create(fridge_id=11,longitude=9.186516,latitude=45.465454)

    #create the user
    user_data={'email':'test@gmail.com', 'first_name': 'TestName', 'last_name':'TestSurname','fridge_id':11, 'password':'debole'}
    url_singup = reverse('user_signup')  
    response=client.post(url_singup,user_data)
    client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])
    return client, user_fridge

def create_super_user(client: APIClient):
    superuser = CustomUser.objects.create_superuser(
        email='test_superuser@gmail.com', 
        password='forte',
        first_name='TestName',
        last_name='TestSurname'
    )
    token, created = Token.objects.get_or_create(user=superuser)

    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client



