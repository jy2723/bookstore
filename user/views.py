from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate
import json
from rest_framework import viewsets
from django.conf import settings
from .models import User
from rest_framework.views import APIView
from django.forms import model_to_dict
from .serializer import RegisterSerializer
from .serializer import LoginSerializer
from .serializer import EmailSerializer
from .serializer import PasswordSerializer
from rest_framework.response import Response
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.reverse import reverse
import jwt
from .models import User
from jwt import PyJWTError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .tasks import send_email_task

# Create your views here.


class RegisterAPI(APIView):  
    @swagger_auto_schema(request_body=RegisterSerializer, responses={201: openapi.Response(description="Register response", examples={
"application/json": {'message': 'string', 'status': 201, 'data': {}}
                         }),400: "Invalid email or password"})   
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            token = RefreshToken.for_user(serializer.instance).access_token
            url = f'{settings.BASE_URL}{reverse("userApi")}?token={token}'
            email = request.data['email']
            subject = 'This is mail from django server'
            message = f'The url \n {url}'
            from_mail = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message,from_mail, recipient_list)
            return Response({'message': 'User registered', 'status': 201, 
                                'data': serializer.data}, status=201)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)

    @swagger_auto_schema(manual_parameters=[openapi.Parameter('token', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)], 
                         responses={200: openapi.Response(description="Response", examples={
                             "application/json": {'message': 'User verified successfully', 'status': 200}
                         }),
                                    400: "Bad Request"}) 
    def get(self, request):
        try:
            token = request.query_params.get('token')
            if not token:
                pass
            payload = jwt.decode(token, key=settings.SIMPLE_JWT.get('SIGNING_KEY'), algorithms=[settings.SIMPLE_JWT.get('ALGORITHM')])
            user = User.objects.get(id=payload['user_id'])
            user.is_verified = True
            user.save()
            return Response({'message': 'User verified successfully', 'status': 200,'token':str(token)}, status=200)
        except PyJWTError:
            return Response({'message': 'Invalid token', 'status': 400}, status=400)
        except User.DoesNotExist:
            return Response({'message': 'User does not exitst', 'status': 400}, status=400)
        
        # User authentication failed
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data in request body', 'status': 400})
        except Exception as e:
            return JsonResponse({'message': str(e), 'status': 400})
        
class LoginAPI(APIView):

    @swagger_auto_schema(request_body=LoginSerializer, 
                         responses={200: openapi.Response(description="Login response", examples={
                             "application/json": {'message': 'string', 'status': 200, 'data': {}}
                         }),
                                    401: "Invalid username or password"})
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            token = RefreshToken.for_user(serializer.instance).access_token
            return Response({'message': 'Login successful', 'status': 200,'token':str(token)}, status=200)
        # User authentication failed
        except Exception as e:
            return Response({'message': str(e), 'status': 400})
        
class ResetPasswordApi(viewsets.ViewSet):
    
    @swagger_auto_schema(request_body=EmailSerializer, 
                         responses={200: openapi.Response(description="Email Sent Successfully", examples={
                             "application/json": {'message': 'An Email is sent', 'status': 200}
                         }),
                                    400: "Bad Request"})
    
    def send_reset_password_link(self, request):
        try:
            email = request.data['email']
            mail = User.objects.filter(email = email).first()
            if(mail):
                token = RefreshToken.for_user(mail).access_token
                url = f'{settings.BASE_URL}{reverse("reset")}?token={token}'
                subject = 'Reset Password Link'
                message = f"""Hi ,This is your reset password link:\n\nPassword Reset Link: {url}"""
                from_mail = settings.EMAIL_HOST_USER
                recipient_list = [email]
                send_mail(subject, message, from_mail, recipient_list)
                return Response({'message': 'An Email is sent', 'status': 200,'token':str(token)}, status=200)
            return Response({'message': 'Email not found', 'status': 404}, status=404)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)
        
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('token', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)],request_body=PasswordSerializer, 
                         responses={200: openapi.Response(description="Password Updated", examples={
                             "application/json": {'message': 'Password Updated Successfully', 'status': 200}
                         }),
                                    400: "Bad Request"})
     
    def change_password(self, request):
        try:
            token = request.query_params.get('token')
            if not token:
                return Response({'message': 'Invalid Token', 'status': 400}, status=400)
            payload = jwt.decode(token, key=settings.SIMPLE_JWT.get('SIGNING_KEY'), algorithms=[settings.SIMPLE_JWT.get('ALGORITHM')])
            new_password = request.data["new_password"]
            user = User.objects.get(id=payload['user_id'])
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password Updated Successfully', 'status': 200}, status=200)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)