from django.contrib.auth import login , logout
from rest_framework import status, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from order.models import Order
from order.serializers import OrderSerializer
from .serializers import UserSerializer
from .serializers import UserLoginSerializer , UserRegisterSerializer , UserSerializer
from .validations import custom_validation 
import jwt , datetime
from dotenv import load_dotenv
import os
from django.utils import timezone
import pytz
from rest_framework.parsers import MultiPartParser, FormParser

load_dotenv()

class UserView(APIView):
    def get(self,request):
        return Response(data="Hello",status=201)

class OneUserView(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (MultiPartParser, FormParser)
    
    def get(self,request, user_id ):
        try:
            user = User.objects.get(user_id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
    # def patch(self, request, user_id):
    #     permission_classes = (permissions.AllowAny,)
    #     try:
    #         user = User.objects.get(user_id=user_id)
    #         print(request.data)
    #         serializer = UserSerializer(user, data=request.data, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except User.DoesNotExist:
    #         return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
   
    def patch(self, request, user_id):
        try:
            user = User.objects.get(user_id=user_id)
            print("Request Data:", request.data)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
class OneUserOrdersView(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, user_id):
        try:
            orders = Order.objects.filter(user_id=user_id)       
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)


class UserRegister(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        valid_data =  custom_validation(request.data)
        serializer = UserRegisterSerializer(data=valid_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(valid_data)
            if user:
                return Response(serializer.data , status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = (SessionAuthentication,)
	
	def post(self, request):
            data = request.data
            serializer = UserLoginSerializer(data=data)

            if serializer.is_valid(raise_exception=True):
                user = serializer.check_user(data)
            egypt_tz = pytz.timezone('Africa/Cairo')
            now = timezone.now().astimezone(egypt_tz)
            payload = {
            'id': user.user_id,
            'exp': now + datetime.timedelta(hours=2),
            'iat': now 
            }
            token = jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')
            
            response = Response(data={ 
                    "message":"Logged in successfully",
                    "data":{
                    "id": user.user_id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone": user.phone,
                    # "image": user.image,
                    # "username": user.username,
                    }})

            response.set_cookie(key='jwt',value=token,httponly=True)
            return response


class UserLogout(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
	
    def post(self, request):
        response = Response()
        response.delete_cookie(key='jwt')
        response.data = {
            "message":"logged out successfully"
        }
        print("Logged out")
        return response


class UserView(APIView):
	# permission_classes = (permissions.IsAuthenticated,)
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)
	
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)

class AdminLogin(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            data = request.data
            serializer = UserLoginSerializer(data=data)

            if serializer.is_valid(raise_exception=True):
                user = serializer.check_admin(data)
            egypt_tz = pytz.timezone('Africa/Cairo')
            now = timezone.now().astimezone(egypt_tz)
            payload = {
            'id': user.user_id,
            'exp': now + datetime.timedelta(hours=2),
            'iat': now 
            }
            token = jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')
            
            response = Response(data={ 
                    "message":"Logged in successfully",
                    "data":{
                    "id": user.user_id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone": user.phone,
                    # "image": user.image,
                    # "username": user.username,
                    }})
            response.set_cookie(key='jwt',value=token,httponly=True)
            return response   
        except:   
            return  Response({"message":"Unautorized !!"},status=status.HTTP_401_UNAUTHORIZED)   