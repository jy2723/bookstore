from django.urls import path
from . import views

resetPasswordSendLink = views.ResetPasswordApi.as_view({
    'post': 'send_reset_password_link',    
})

resetPassword = views.ResetPasswordApi.as_view({
    'post': 'change_password'
})

urlpatterns = [
    path('register', views.RegisterAPI.as_view(), name='userApi'),
    path('login', views.LoginAPI.as_view(), name='login'),
    path('reset/', resetPasswordSendLink, name='reset'),
    path('changePassword/', resetPassword, name='change')
]

