from datetime import date, timedelta
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Fridge, Product,Parameter
from .serializers import FridgeSerializer, ProductSerializer, ParameterSerializer, CustomUserSerializer, CustomUserSignUpSerializer, LoginSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Fridge, Product
from .serializers import FridgeSerializer, ProductSerializer
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view

#for admin
class FridgeList(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve all the fridges from the database",
        responses={200: 'Ok'}
    )
    def get(self, request):
        fridges = Fridge.objects.all()
        serializer = FridgeSerializer(fridges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    @swagger_auto_schema(
        operation_description="Create a new fridge",
        request_body=FridgeSerializer,
        responses={201: 'Created', 400: 'Bad Request'}
    )
    def post(self, request):
            serializer=FridgeSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status= status.HTTP_400_BAD_REQUEST)

class FridgeDetail(APIView):
    @swagger_auto_schema(
        operation_description="Retrive info about a fridge",
        responses={200: 'Ok', 404: "Fridge doesn't exist"}
    )
    def get(self, request, pk_fridge):
        fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        serializer = FridgeSerializer(fridge)
        return Response(serializer.data,status=status.HTTP_200_OK)

class FridgeProductList(APIView):
    @swagger_auto_schema(
        operation_description="Insert a new product in a fridge.If fridge_id is different from the one in the url, the url one is considered the valid one",
        request_body=ProductSerializer,
        responses={201: 'Created', 404:"The fridge doesn't exist", 400: 'Bad Request'}
    )
    def post(self,request,pk_fridge):
        fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)

        data = request.data.copy()
        data['fridge'] = pk_fridge
        serializer=ProductSerializer(data=data) 

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    @swagger_auto_schema(
        operation_description="Retrieve all the products from a fridge",
        responses={200: 'Ok', 404:"The fridge doesn't exist"}
    )
    def get(self,request,pk_fridge):
        fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)

        product = Product.objects.filter(fridge=pk_fridge)
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FridgeProductDetail(APIView):
    @swagger_auto_schema(
        operation_description="Delete a product from a fridge. If fridge_id is different from the one in the url, the url one is considered the valid one.",
        responses={404:"The fridge or the product don't exist"}
    )
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
    @swagger_auto_schema(
        operation_description="Update a product of a fridge.If fridge_id is different from the one in the url, the url one is considered the valid one",
        request_body=ProductSerializer,
        responses={201: 'Created', 404:"The fridge or the product don't exist", 400: 'Bad Request'}
    )
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

class FridgeExpiringProduct(APIView):
    @swagger_auto_schema(
        operation_description="Retrive all the expiring products in a fridge",
        responses={200: 'Ok', 404: "Fridge does't exist"}
    )
    def get(self, request,pk_fridge):
        existing_fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        tomorrow = date.today() + timedelta(days=1)
        
        product = Product.objects.filter(fridge=existing_fridge,expire_date=tomorrow)
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FridgeParameter(APIView):
    @swagger_auto_schema(
        operation_description="Retrive the last (most recent) 20 sampled parameters",
        responses={200: 'Ok', 404: "Fridge does't exist"}
    )
    def get(self, request, pk_fridge):
        existing_fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        parameters=Parameter.objects.filter(fridge=existing_fridge).order_by('sampling_date')[:20]
        return Response(ParameterSerializer(parameters, many=True).data, status=status.HTTP_200_OK)
    @swagger_auto_schema(
        operation_description="Post a new set of parameters for a fridge.If fridge_id is different from the one in the url, the url one is considered the valid one",
        request_body=ParameterSerializer,
        responses={201: 'Created', 400: 'Bad Request',404:"Fridge does't exist"}
    )
    def post(self,request, pk_fridge):
        existing_fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        data=request.data.copy()
        data['fridge']=pk_fridge
        serializer=ParameterSerializer(data=data) 

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    operation_description="Login function",
    method='post',
    request_body=LoginSerializer,
    responses={200: 'Authenticated', 401: "Login error"}
)
@api_view(['POST'])
def login(request):

    login_data_serialized=LoginSerializer(data=request.data)
    if login_data_serialized.is_valid():
        user=login_data_serialized.validate(request.data)
    
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"token": token.key},
                status=status.HTTP_200_OK
            )
    
    return Response(
        {"error": login_data_serialized.errors},
        status=status.HTTP_401_UNAUTHORIZED
    )


@swagger_auto_schema(
    operation_description="New user signup",
    method='post',
    request_body=CustomUserSignUpSerializer,
    responses={201: 'Created', 400: 'Bad Request', 500: 'Problems with token'}
)
@api_view(['POST'])
def signup(request):
    user_serialized = CustomUserSignUpSerializer(data=request.data)
    if user_serialized.is_valid():
        user = user_serialized.save()
        try:
            token, created = Token.objects.get_or_create(user=user)
        except Exception as e:
            return Response(
                {"error": "Error creating authentication token", "details": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(
            { "token": token.key, "user": CustomUserSerializer(user).data},status=status.HTTP_201_CREATED
        )
    else:
        return Response(
            {"errors": user_serialized.errors},status=status.HTTP_400_BAD_REQUEST
        )