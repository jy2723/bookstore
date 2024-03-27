from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookApi.as_view(),name="book_api"),
]