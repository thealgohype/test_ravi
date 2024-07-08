from django.urls import path
from . import views

urlpatterns = [
    path('v1/auth/login/google/', views.GoogleLoginApi.as_view(), name='login-with-google'),
    path('getall/', views.get_user_all_records, name='get_user'),
    path('add/', views.add_test, name='add'),
    path('get/', views.get_grouped_data, name='get_group_user')
]