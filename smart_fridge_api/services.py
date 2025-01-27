from datetime import date, timedelta
from .models import Fridge, Product,Parameter
from .serializers import FridgeSerializer, ProductSerializer, ParameterSerializer, CustomUserSerializer, CustomUserSignUpSerializer, LoginSerializer


def mid_day_update():
    #delete products expired the day before
    yesterday = date.today() - timedelta(days=1)
    products_expired_yesterday=Product.objects.filter(expire_date=yesterday)
    products_expired_yesterday.delete()
    #delete products given to charity during the morning
    today = date.today()
    products_given_to_charity=Product.objects.filter(expire_date=today, toCharity=True)
    products_given_to_charity.delete()
