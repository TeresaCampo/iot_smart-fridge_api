from datetime import date, timedelta
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Fridge, Product,Parameter
from .serializers import FridgeSerializer, ProductSerializer, ParameterSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Fridge, Product
from .serializers import FridgeSerializer, ProductSerializer

def index(request):
    return HttpResponse("This is the smart fridge API.")

#                           for admin
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

#get /fridges/<int:pk>/   -->retrieve info about a specific fridge(id,address,city,country)
class FridgeDetail(APIView):
    def get(self, request, pk_fridge):
        fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        serializer = FridgeSerializer(fridge)
        return Response(serializer.data,status=status.HTTP_200_OK)

#post /fridges/<int:pk>/products   --> insert a product in a fridge
#get /fridges/<int:pk>/products    --> retieve all the products in a fridge
class FridgeProductList(APIView):
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
        product = Product.objects.filter(fridge=pk_fridge)
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#put /fridges/<int:pk_fridge>/products/<str:barcode>/<str:expire_date>   -->update a product(barcode,expire_date) from a fridge
    #in the body put all the data of the products
    #if fridge_id is different from the one in the url, the url one is considered the valid one
#delete /fridges/<int:pk_fridge>/products/<str:barcode>/<str:expire_date>   -->delete a product(barcode,expire_date) from a fridge
class FridgeProductDetail(APIView):
    def delete(self,request,pk_fridge,barcode,expire_date):
        #check if fridge exists
        fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)

        #check if product exists
        product_to_be_deleted = Product.objects.filter(fridge=fridge, barcode=barcode, expire_date=expire_date).first()
        if product_to_be_deleted is None:
            return Response({'message': 'Product is not present in the database.'}, status=status.HTTP_404_NOT_FOUND)
        
        #delete the object
        product_to_be_deleted.delete()
        return Response({'status': 'success', 'message': 'Product deleted successfully.'}, status=status.HTTP_200_OK)
    def put(self,request,pk_fridge,barcode,expire_date):
        #check if fridge exists
        fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)

        #check if product exists
        product_to_be_updates = Product.objects.filter(fridge=fridge, barcode=barcode, expire_date=expire_date).first()
        if product_to_be_updates is None:
            return Response({'message': 'Product is not present in the database.'}, status=status.HTTP_404_NOT_FOUND)

        #update it
        updated_data = request.data.copy()
        updated_data['fridge'] = pk_fridge
        serializer = ProductSerializer(product_to_be_updates, data=updated_data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success'},status=status.HTTP_200_OK)
        else:
            return Response(
                {'status': 'error', 'message': 'Invalid data.', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

#get /fridges/<int:pk>/expiringProducts    -->retieve all the expring products in a fridge
class FridgeExpiringProduct(APIView):
    def get(self, request,pk_fridge):
        existing_fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        tomorrow = date.today() + timedelta(days=1)
        
        product = Product.objects.filter(fridge=existing_fridge,expire_date=tomorrow)
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#get /fridges/<int:pk>/parameters --> retrive last 20 sampled parameters
#post /fridges/<int:pk>/parameters -->post a new set of parameters
class FridgeParameter(APIView):
    def get(self, request, pk_fridge):
        existing_fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        parameters=Parameter.objects.filter(fridge=existing_fridge).order_by('sampling_date')[:20]
        return Response(ParameterSerializer(parameters, many=True).data, status=status.HTTP_200_OK)
    def post(self,request, pk_fridge):
        existing_fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        data=request.data.copy()
        data['fridge']=pk_fridge
        serializer=ParameterSerializer(data=data) 

        if serializer.is_valid():
            serializer.save()
            return Response({'status':'success'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status':'error'}, status=status.HTTP_400_BAD_REQUEST)
   

        