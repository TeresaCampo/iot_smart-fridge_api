from datetime import date, timedelta
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Fridge, Product
from .serializers import FridgeSerializer, ProductSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Fridge, Product
from .serializers import FridgeSerializer, ProductSerializer

def index(request):
    return HttpResponse("This is the smart fridge API.")

#get fridges/               --> read all the fridges in the database
#post fridges/              --> insert a new fridge in the database
class FridgeList(APIView):
    def get(self, request):
        fridges = Fridge.objects.all()
        serializer = FridgeSerializer(fridges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
            serializer=FridgeSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status":"error"}, status= status.HTTP_400_BAD_REQUEST)

#get /fridges/<int:pk>/   -->retrieve info about a specific fridge
class FridgeDetail(APIView):
    def get(self, request, pk_fridge):
        fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        serializer = FridgeSerializer(fridge)
        return Response(serializer.data,status=status.HTTP_200_OK)

#post /fridges/<int:pk>/products   --> insert a product in a fridge
#get /fridges/<int:pk>/products    -->retieve all the products in a fridge
class FridgeProduct(APIView):
    def post(self,request,pk_fridge):
        fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)

        data = request.data.copy()
        data['fridge'] = pk_fridge
        serializer=ProductSerializer(data=data) 

        if serializer.is_valid():
            serializer.save()
            return Response({'status':'success'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status':'error'}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request,pk_fridge):
        product = Product.objects.all()
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#get /fridges/<int:pk>/expiringProducts    -->retieve all the products in a fridge
class FridgeExpiringProduct(APIView):
    def get(self, request,pk_fridge):
        fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        tomorrow = date.today() + timedelta(days=1)
        
        product = Product.objects.filter(expire_date=tomorrow)
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
