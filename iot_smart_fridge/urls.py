from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/', include('smart_fridge_api.urls')),
    path('admin/', admin.site.urls),
]
