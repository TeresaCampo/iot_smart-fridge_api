from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

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

#customized user
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is needed')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)
class CustomUser(AbstractBaseUser):
    #my customize fields, user identified by email
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    fridge = models.ForeignKey(Fridge, on_delete=models.CASCADE,null=True, blank=True)

    #django utils fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)  # Questo è necessario per gestire il superuser
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        if self.fridge:
            return f'User {self.email} associated to fridge {self.fridge.fridge_id}'
        else:
            return f'User {self.email} (no fridge)'    
     # Implementa i metodi di permesso
    def has_perm(self, perm, obj=None):
        "Return True if the user has the given permission."
        return self.is_superuser or self.is_staff
    def has_module_perms(self, app_label):
        "Return True if the user has permissions for the given app."
        return self.is_superuser or self.is_staff