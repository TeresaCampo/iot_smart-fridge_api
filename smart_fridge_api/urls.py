from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    #get fridges/               --> read all the fridges in the database
    #post fridges/              --> insert a new fridge in the database
    path('fridges/', views.FridgeList.as_view(), name='fridge_list'),
    path('fridges/<int:pk>/', views.FridgeDetail.as_view(), name='fridge_detail'),
]
#for user

#get /fridges/<int:pk>/expiringProducts
#get /fridges/<int:pk>/products

#post /fridges/<int:pk>/parameters (umidità e temperatura)
#get /fridges/<int:pk>/parameters (umidità e temperatura)

#post /fridges/<int:pk>/insertedProduct
#post /fridges/<int:pk>/removedProduct

#login


