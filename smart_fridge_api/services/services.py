from datetime import date, timedelta
from ..models import Fridge, Product,Parameter
from .ottimizzatore_path import start

def mid_day_routine():
    #delete products expired the day before
    yesterday = date.today() - timedelta(days=1)
    Product.objects.filter(expire_date=yesterday).exclude(fridge__fridge_id=1).delete()

    #delete products given to charity during the morning
    today = date.today()
    Product.objects.filter(expire_date=today, toCharity=True).exclude(fridge__fridge_id=1).delete()

    #set toCharity_updated_today a False for every fridge
    Fridge.objects.update(toCharity_updated_today=False)


def morning_routine():
    #collect addresses of people who set True to toCharity_updated_today
    fridges_with_toCharity_products = Fridge.objects.filter(product__toCharity=True).distinct()
    print(fridges_with_toCharity_products)
    fridges_latitude_longitude= [f"{fridge.latitude}, {fridge.longitude}" for fridge in fridges_with_toCharity_products]

    #calculate best route and send it to voluteers via telegram
    start(fridges_latitude_longitude)
    
    #not allow other users to give product to charity from now to mid day
    Fridge.objects.update(toCharity_updated_today=True)

