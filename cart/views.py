from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializer import CartSerializer, ItemSerializer
from .models import Cart, CartItems
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.
class CartApi(APIView):
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'book': openapi.Schema(type=openapi.TYPE_INTEGER),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
        },
        required=['book','quantity']
    ),
    responses={
        201: openapi.Response(
            description="Note Created",
            examples={"application/json": {'message': 'Cart Deleted Successfully!', 'status': 201}}
        ),
        400: "Bad Request",
        401: "Unauthorized"
    }
    )
    def post(self, request):
        try:
            request.data["user"] = request.user.id
            serializer = CartSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Added Item to Cart', 'status': 201, 'data': serializer.data}, status=201)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Cart items fetched", examples={
                "application/json": {'message': 'Successfully Fetched Cart Items', 'status': 200, 'Cart Items': []}
            }),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def get(self, request):
        try:
            user_id = request.user.id
            cart = Cart.objects.filter(user_id=user_id, is_ordered=False).first()
            if cart:
                cart_items = CartItems.objects.filter(cart=cart)
                serializer = ItemSerializer(cart_items, many=True)
                return Response({'message': 'Successfully Fetched Cart Items', 'status': 200, 'Cart Items': serializer.data}, status=200)
            else:
                return Response({'message': 'Cart not found', 'status': 404}, status=404)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('cart_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True, description='ID of the cart to delete')
        ],
        responses={
            200: openapi.Response(description="Cart deleted", examples={
                "application/json": {'message': 'Cart Deleted Successfully!', 'status': 200}
            }),
            400: "Bad Request"
        }
    )      
    
    
    def delete(self, request):
        try:
            user_id = request.user.id
            cart_id = request.query_params.get('cart_id')
            if cart_id is None:
                return Response({'message': 'Cart ID is not provided', 'status': 400}, status=400)
            cart = Cart.objects.get(user_id = user_id, id=cart_id)
            cart.delete()
            return Response({'message': 'Cart Deleted Successfully!', 'status': 200}, status=200)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)
        
        
