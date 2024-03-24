from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Books
from user.models import User
from .serializer import BooksSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import PermissionDenied

class BookApi(APIView):
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    @swagger_auto_schema(request_body=BooksSerializer, responses={201: openapi.Response(description="Book Added", examples={
                             "application/json": {'message': 'Book Added Successfully', 'status': 201, 'data': {}}
                         }),
                                    400: "Bad Request"})
    
    def post(self, request):
        try:
            request.data['user'] = request.user.id
            serializer = BooksSerializer(data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Book Added Successfully!', 'status': 201, 
                            'data': serializer.data}, status = 201)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status = 400)
        
    @swagger_auto_schema(responses={200: openapi.Response(description="Books Fetched Successfully!", examples={
                             "application/json": {'message': 'Books Fetched Successfully!', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})
    
    def get(self, request):
        try:
            books = Books.objects.all()
            serializer = BooksSerializer(instance=books, many=True)
            return Response({'message': 'Books Fetched Successfully!', 'status': 200, 'books': serializer.data}, status=200)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status = 400)
        
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'book_id':openapi.Schema(type=openapi.TYPE_NUMBER),
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'author': openapi.Schema(type=openapi.TYPE_STRING),
            'price': openapi.Schema(type=openapi.TYPE_NUMBER),
            'quantity': openapi.Schema(type=openapi.TYPE_NUMBER),
        },
        required=['book_id','title', 'author', 'price', 'quantity']
    ),
    responses={
        201: openapi.Response(
            description="Note Created",
            examples={"application/json": {'message': 'Book Updated successfully', 'status': 201, 'data': {}}}
        ),
        400: "Bad Request",
        401: "Unauthorized"
    }
)
    
    def put(self, request):
        try:
            request.data['user'] = request.user.id
            book = Books.objects.get(id=request.data['book_id'])
            serializer = BooksSerializer(instance=book, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Book Updated Successfully!', 'status': 200, 
                            'data': serializer.data}, status=200)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)
        
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)], responses={200: openapi.Response(description="Response", examples={
                             "application/json": {'message': 'Successfully Deleted Data','data':{}, 'status': 200}
                         }),
                                    400: "Bad Request", 401:"Unauthorized",404:"Notes not found"}) 
    
    def delete(self, request):
        try:
            if request.user.is_superuser:
                book_id = request.query_params.get('id')
                books = Books.objects.get(id = book_id)
                books.delete()
                return Response({'message': 'Book Deleted Successfully', 'status': 200},status=200)
            raise PermissionDenied("Access denied")
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)