from django.db import models


'''
smart_fridge(fridge_id, address, city, country)
PK(fridge_id)

product(fridge_id, barcode, expire_date, name)
PK(id autogenerato)
FK fridge_id REFERENCES smart_fridge

parameters(fridge_id, humidity, temperature, sampling_date)
PK(id autogenerato) <-avrei voluto(fridge_id, sampling_data), ma Django non offre composite PK
FK fridge_id REFERENCES smart_fridge
'''
class Fridge(models.Model):
    fridge_id = models.IntegerField(primary_key=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"Fridge {self.fridge_id} in {self.city}, {self.country}"

class Parameter(models.Model):
    fridge = models.ForeignKey(Fridge, on_delete=models.CASCADE)
    humidity=models.FloatField(null=True)
    temperature=models.FloatField(null=True)
    sampling_date = models.DateTimeField()

    def __str__(self):
        return f"Parameters of fridge {self.fridge.fridge_id} in {self.sampling_date.strftime('%Y-%m-%d %H:%M')} (Humidity: {self.humidity}) - (Temperature: {self.temperature})"

class Product(models.Model):
    fridge = models.ForeignKey(Fridge, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=100)
    expire_date = models.DateField()
    name = models.CharField(max_length=100)
    
    def __str__(self):
            return f"{self.name} (Barcode: {self.barcode}) - Expires on {self.expire_date}"

