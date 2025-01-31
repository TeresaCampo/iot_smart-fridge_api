from django.core.management.base import BaseCommand
from ...models import *
from datetime import datetime, timedelta, date

class Command(BaseCommand):
    help = "Resetta il database e popola con nuovi dati"

    def handle(self, *args, **kwargs):
        today= date.today()
        tomorrow = date.today() + timedelta(days=1)
        yesterday = date.today() + timedelta(days=1)

        #delete existing products and parameters associated to fridges
        Product.objects.all().delete()
        Parameter.objects.all().delete()
        #delete extra fridges
        Fridge.objects.exclude(fridge_id__in=[1, 2, 3]).delete()

        #create new products and set toCharity_update_today to default for every fridge
        fridge1 = Fridge.objects.get(fridge_id=1)
        Fridge.objects.filter(fridge_id=1).update(toCharity_updated_today=False)
        Product.objects.create(fridge=fridge1,barcode="5678930", expire_date=today+timedelta(days=4),name="Latte")      #not expiring yet
        Product.objects.create(fridge=fridge1,barcode="2307450", expire_date=tomorrow,name="Burro")                     #expiring tomorrow
        Product.objects.create(fridge=fridge1,barcode="3429762", expire_date=today+timedelta(days=3),name="Mozzarelle") #not expiring yet  

        fridge2 = Fridge.objects.get(fridge_id=2)
        Fridge.objects.filter(fridge_id=2).update(toCharity_updated_today=True)
        Product.objects.create(fridge=fridge2,barcode="3429762", expire_date=tomorrow,name="Mozzarelle")                #expiring tomorrow
        Product.objects.create(fridge=fridge2,barcode="5678930", expire_date=yesterday,name="Latte")                    #expired
        Product.objects.create(fridge=fridge2,barcode="7843259", expire_date=today+timedelta(days=3),name="Uova")       #not epxpiring yet
            
        fridge3 = Fridge.objects.get(fridge_id=3)
        Fridge.objects.filter(fridge_id=1).update(toCharity_updated_today=True)
        Product.objects.create(fridge=fridge3,barcode="67029817", expire_date=today,name="Philadelphia")                #expiring today
        Product.objects.create(fridge=fridge3,barcode="5678930", expire_date=tomorrow,name="Latte")                     #expiring tomorrow

        self.stdout.write(self.style.SUCCESS("Database initialized with default values"))
        
        #users associated to fridges 1,2,3 are always the same:
        #fridge 1 -> Anna Bianchini, token: c5c90de5802459f2e9b267f7f63857ed9c1c6e7b
        #fridge 2 -> Andrea Rossi, token: 23dc9513ea976e202f306fd7d93c5093a066c5f0
        #fridge 3 -> Maria Verdi, token: 74d7cf3d048ba4f92ef2eb6352e7326e0996c56e

        #superuser
        # campoteresa.2002@gmail.com -> 62aa1bd2271eedd587232a3259f262fa5b578d88
