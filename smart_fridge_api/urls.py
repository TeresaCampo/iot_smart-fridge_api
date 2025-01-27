from django.urls import path
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

TokenAuth = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description="Token di autorizzazione (ad esempio: 'Token <your_token>')",
    type=openapi.TYPE_STRING,
)

#Documentation page header
schema_view = get_schema_view(
   openapi.Info(
      title="Smart fridge API",
      default_version='v1',
      contact=openapi.Contact(email="campoteresa.2002@gmail.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    #API documentation
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-docs'),

    #get fridges/               --> read all the fridges in the database
    #post fridges/              --> insert a new fridge in the database
    path('fridges/', views.FridgeManager.as_view(), name='fridge_list'),
    #get /fridges/<int:pk>/   -->retrieve info about a specific fridge
    path('fridges/<int:pk_fridge>/', views.FridgeDetail.as_view(), name='fridge_detail'),
    
    #post /fridges/<int:pk>/products   --> insert a product in a fridge
    #get /fridges/<int:pk>/products    -->retieve all the products in a fridge
    path('fridges/<int:pk_fridge>/products', views.FridgeProductList.as_view(), name='fridge_product_list'),
    #delete /fridges/<int:pk_fridge>/products/<str:barcode>/<str:expire_date>   -->delete a product(barcode,expire_date) of a fridge
    path('fridges/<int:pk_fridge>/products/<str:barcode>/<str:expire_date>', views.FridgeProductDetail.as_view(), name='fridge_product_detail'),
   
    
    #get /fridges/<int:pk>/expiringProducts    -->retieve all the products in a fridge
    path('fridges/<int:pk_fridge>/expiringProducts', views.FridgeExpiringProduct.as_view(), name='fridge_expiring_product'),
    #post /fridges/<int:pk>/expiringProducts/<str:barcode>  -->inform backend if the product is going to be donated or not
    path('fridges/<int:pk_fridge>/expiringProducts/<str:barcode>', views.donate_product, name='fridge_expiring_product_donate'),
    
    #get /fridges/<int:pk>/parameters --> retrive last 20 sampled parameters
    #post /fridges/<int:pk>/parameters -->post a new set of parameters
    path('fridges/<int:pk_fridge>/parameters', views.FridgeParameter.as_view(), name='fridge_parameter'),
    
    #post /singup
    path('signup', views.signup, name='user_signup'),
    #post /login
    path('login', views.login, name='user_login')
]


