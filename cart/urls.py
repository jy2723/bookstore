from django.urls import path
from .views import CartApi,OrderedCartApi

urlpatterns = [
    path('cart/', CartApi.as_view(), name='cart-api'),  
    path('cart/order', OrderedCartApi.as_view(), name='order-api'),
]
