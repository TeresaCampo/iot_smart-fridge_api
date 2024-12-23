from django.contrib import admin
from .models import Product, Fridge, Parameter, CustomUser
from django.contrib.auth.models import User

# Register your models here.
admin.site.register(Product)
admin.site.register(Fridge)
admin.site.register(Parameter)
admin.site.register(CustomUser)

