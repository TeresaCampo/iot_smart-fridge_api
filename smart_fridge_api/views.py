
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
        return Response(serializer.data)
    
    def post(self, request):
            serializer=FridgeSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status":"error"}, status= status.HTTP_400_BAD_REQUEST)

#post /fridges/<int:pk>/products/<int:pk>
#get /fridges/<int:pk>/products         -->prendere tutti i prodotti in un frigo
class FridgeDetail(APIView):
    def get(self, request, pk):
        fridge=get_object_or_404(Fridge,pk=pk)
        serializer = FridgeSerializer(fridge)
        return Response(serializer.data)
        
    
   
    