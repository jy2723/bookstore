from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializer import CartSerializer, ItemSerializer
from .models import Cart, CartItems
from book.models import Books
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
            'book_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
        },
        required=['book_id','quantity']
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
        
        
class OrderedCartApi(APIView):
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Ordered cart items fetched", examples={
                "application/json": {'message': 'Successfully Fetched Ordered Cart Items', 'status': 200, 'Ordered Cart Items': []}
            }),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def get(self, request):
        try:
            user_id = request.user.id

            ordered_carts = Cart.objects.filter(user_id=user_id, is_ordered=True)

            if not ordered_carts:
                return Response({'message': 'No ordered carts found for this user', 'status': 404}, status=404)

            all_cart_data = []

            for cart in ordered_carts:
                cart_items = CartItems.objects.filter(cart=cart)
                serializer = ItemSerializer(cart_items, many=True)
                cart_data = {
                    'cart_id': cart.id,  
                    'cart_items': serializer.data
                }
                all_cart_data.append(cart_data)

            return Response({'message': 'Successfully Fetched All Ordered Carts and Items', 'status': 200, 'Ordered Carts': all_cart_data}, status=200)

        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)



    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Ordered successfully!", examples={
                "application/json": {'message': 'Cart marked as Ordered', 'status': 200, 'Ordered Cart Items': []}
            }),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def post(self, request):
        try:
            user_id = request.user.id
            cart = Cart.objects.filter(user_id=user_id, is_ordered=False).first()

            if not cart:
                return Response({'message': 'Cart not found for this user', 'status': 404}, status=404)

            cart_items = CartItems.objects.filter(cart=cart)
            books = Books.objects.filter(id__in=cart_items.values_list('book_id', flat=True))

            if any(book.quantity < cart_items.filter(book=book).count() for book in books):
                return Response({'message': 'Insufficient stock for some items', 'status': 400}, status=400)

            cart.is_ordered = True
            cart.save()

            for cart_item in cart_items:
                book = cart_item.book  
                book.quantity -= cart_item.quantity  
                book.save()

            # Retrieve details of the ordered cart
            serializer = CartSerializer(cart)

            return Response({'message': 'Cart marked as Ordered', 'status': 200, 'data': serializer.data}, status=200)

        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)




    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('cart_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True, description='ID of the ordered cart to delete')
        ],
        responses={
            200: openapi.Response(description="Ordered cart deleted", examples={
                "application/json": {'message': 'Ordered Cart Deleted Successfully!', 'status': 200}
            }),
            400: "Bad Request"
        }
    )      
    def delete(self, request):
        try:
            user_id = request.user.id
            cart_id = request.query_params.get('cart_id')

            if cart_id is None:
                return Response({'message': 'Ordered Cart ID is not provided', 'status': 400}, status=400)

            cart = Cart.objects.get(user_id=user_id, id=cart_id, is_ordered=True)

            cart_items = CartItems.objects.filter(cart=cart)
            books = Books.objects.filter(id__in=cart_items.values_list('book_id', flat=True))

            for cart_item in cart_items:
                book = cart_item.book 
                book.quantity += cart_item.quantity  
                book.save()

            cart.delete()

            return Response({'message': 'Ordered Cart Deleted Successfully! Book quantities updated.', 'status': 200}, status=200)

        except Cart.DoesNotExist:
            return Response({'message': 'Ordered Cart not found', 'status': 404}, status=404)

        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)
