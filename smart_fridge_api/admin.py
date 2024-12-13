from django.contrib import admin
from .models import Product, Fridge, Parameter

# Register your models here.
admin.site.register(Product)
admin.site.register(Fridge)
admin.site.register(Parameter)


