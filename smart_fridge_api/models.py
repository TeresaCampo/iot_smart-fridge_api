from django.db import models


'''
smart_fridge(fridge_id, address, city, country)

product(fridge_id, barcode, expire_date, name)
FK fridge_id REFERENCES smart_fridge
'''
class Fridge(models.Model):
    fridge_id = models.IntegerField(primary_key=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"Fridge {self.fridge_id} in {self.city}, {self.country}"


class Product(models.Model):
    fridge = models.ForeignKey(Fridge, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=100)
    expire_date = models.DateField()
    name = models.CharField(max_length=100)
    
    def __str__(self):
            return f"{self.name} (Barcode: {self.barcode}) - Expires on {self.expire_date}"




