from datetime import date, timedelta
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from .models import Fridge, Product,Parameter
from .serializers import FridgeSerializer, ProductSerializer, ParameterSerializer, CustomUserSerializer, CustomUserSignUpSerializer, LoginSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Fridge, Product
from .serializers import FridgeSerializer, ProductSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view

#----------------------CREATE AND GET FRIDGES----------------------------------------
class FridgeManager(APIView):
    permission_classes = [IsAdminUser]
    @swagger_auto_schema(
        operation_description="For admin(superuser only)\nRetrieve all the fridges from the database.",
        responses={200: 'Ok', 401: 'Not authenticated as superuser'},
    )
    def get(self, request):
        fridges = Fridge.objects.all()
        serializer = FridgeSerializer(fridges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="For admin(superuser only)\nCreate a new fridge.",
        request_body=FridgeSerializer,
        responses={201: 'New fridge created', 400: 'Bad request body', 401: 'Not authenticated as superuser'}
    )
    def post(self, request):
            serializer=FridgeSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status= status.HTTP_400_BAD_REQUEST)

#----------------------GET INFO ABOUT A FRIDGE----------------------------------------
class FridgeDetail(APIView):
    @swagger_auto_schema(
        operation_description="Retrive info about a fridge.",
        responses={200: 'Ok', 404: "Fridge doesn't exist", 401: 'Not authenticated as user'}
    )
    def get(self, request, pk_fridge):
        fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        serializer = FridgeSerializer(fridge)
        return Response(serializer.data,status=status.HTTP_200_OK)

#----------------------CREATE, DELETE OR UPDATE A PRODUCT, GET PRODUCTS----------------------------------------
class FridgeProductList(APIView):
    @swagger_auto_schema(
        operation_description="Insert a new product in the fridge. The valid fridge_id is the one in the url.",
        request_body=ProductSerializer,
        responses={201: 'Created', 404:"The fridge doesn't exist", 400: 'Bad request body', 401: 'Not authenticated as user'}
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
        operation_description="Retrieve all the products from the fridge.",
        responses={200: 'Ok', 404:"The fridge doesn't exist", 401: 'Not authenticated as user'}
    )
    def get(self,request,pk_fridge):
        fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)

        product = Product.objects.filter(fridge=pk_fridge)
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FridgeProductDetail(APIView):
    @swagger_auto_schema(
        operation_description="Delete a product from the fridge. The valid fridge_id is the one in the url.",
        responses={200:"Product succesfully deleted from the fridge",404:"The fridge or the product don't exist", 401: 'Not authenticated as user'}
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
        operation_description="Update a product of a fridge.\nThe url contains the barcode and the expire_date of the product to be updated.\nThe body contains the new info about the product.\nThe valid fridge_id is the one in the url.",
        request_body=ProductSerializer,
        responses={201: 'Product succesfully updated', 404:"The fridge or the product don't exist", 400: 'Bad request body',401: 'Not authenticated as user'}
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

#----------------------GET EXPIRING PRODUCTS AND FLAG TOCHARITY----------------------------------------
class FridgeExpiringProduct(APIView):
    @swagger_auto_schema(
        operation_description="Retrive all the expiring products from a fridge.\nIf the request has already been sent the current day, the response is 304 not modified.",
        responses={304:'Already checked today',200: 'Ok', 404: "Fridge does't exist",401: 'Not authenticated as user'}
    )
    def get(self, request,pk_fridge):
        existing_fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        today=date.today()

        if(existing_fridge.last_charity_update<today):  #check expiring products
            tomorrow = date.today() + timedelta(days=1)
            existing_fridge.last_charity_update=date.today()
            product = Product.objects.filter(fridge=existing_fridge,expire_date=tomorrow)
            serializer = ProductSerializer(product, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Already checked today.'}, status=status.HTTP_304_NOT_MODIFIED)

@swagger_auto_schema(
    operation_description="Set the product as product to be donated.",
    method='post',
    request_body=CustomUserSignUpSerializer,
    responses={200: 'Succesfully updated',404: 'Bad request body', 500: 'Problems with token'}
)
@api_view(['POST'])
def donate_product(request,pk_fridge,barcode):
        #check if fridge exists
        fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        tomorrow = date.today() + timedelta(days=1)

        #check if product exists
        product_to_be_donated = Product.objects.filter(fridge=fridge, barcode=barcode, expire_date=tomorrow).first()
        if product_to_be_donated is None:
            return Response({'message': 'Product is not present in the database.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            product_to_be_donated.toCharity = True  
            product_to_be_donated.save()
            return Response( status=status.HTTP_200_OK)

#----------------------GET TEMP/HUM PARAMETERS----------------------------------------
class FridgeParameter(APIView):
    @swagger_auto_schema(
        operation_description="Retrive the last (most recent) 20 sampled parameters",
        responses={200: 'Ok', 404: "Fridge does't exist", 401: 'Not authenticated as user'}
    )
    def get(self, request, pk_fridge):
        existing_fridge=get_object_or_404(Fridge,fridge_id=pk_fridge)
        parameters=Parameter.objects.filter(fridge=existing_fridge).order_by('sampling_date')[:20]
        return Response(ParameterSerializer(parameters, many=True).data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Insert a new set of parameters of the fridge. The valid fridge_id is the one in the url.",
        request_body=ParameterSerializer,
        responses={201: 'Parameters succesfully saved.', 400: 'Bad request body',404:"Fridge does't exist", 401: 'Not authenticated as user'}
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

#----------------------LOGIN AND SINGUP----------------------------------------
@swagger_auto_schema(
    operation_description="Login.",
    method='post',
    request_body=LoginSerializer,
    responses={200: 'Authenticated (returns token and user_fridge_id)', 401: "Login error"}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    login_data_serialized=LoginSerializer(data=request.data)
    if login_data_serialized.is_valid():
        user=login_data_serialized.validate(request.data)
    
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"token": token.key, "user_fridge_id": user.fridge.fridge_id},
                status=status.HTTP_200_OK
            )
    
    return Response(
        {"error": login_data_serialized.errors},
        status=status.HTTP_401_UNAUTHORIZED
    )

@swagger_auto_schema(
    operation_description="New user signup.\nThe fridge should exist in the database(it is created when the fridge is sold).",
    method='post',
    request_body=CustomUserSignUpSerializer,
    responses={201: 'New user succesfully created', 400: 'Bad request body', 500: 'Problems with token'}
)
@api_view(['POST'])
@permission_classes([AllowAny])
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


