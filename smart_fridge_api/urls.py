from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    #get fridges/               --> read all the fridges in the database
    #post fridges/              --> insert a new fridge in the database
    path('fridges/', views.FridgeList.as_view(), name='fridge_list'),
    #get /fridges/<int:pk>/   -->retrieve info about a specific fridge
    path('fridges/<int:pk_fridge>/', views.FridgeDetail.as_view(), name='fridge_detail'),
    #post /fridges/<int:pk>/products   --> insert a product in a fridge
    #get /fridges/<int:pk>/products    -->retieve all the products in a fridge
    path('fridges/<int:pk_fridge>/products', views.FridgeProduct.as_view(), name='fridge_product'),
    #get /fridges/<int:pk>/expiringProducts    -->retieve all the products in a fridge
    path('fridges/<int:pk_fridge>/expiringProducts', views.FridgeExpiringProduct.as_view(), name='fridge_expiring_product'),


]

#post /fridges/<int:pk>/parameters (umidità e temperatura)
#get /fridges/<int:pk>/parameters (umidità e temperatura)

#login


