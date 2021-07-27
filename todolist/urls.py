from django.contrib.auth.views import LogoutView
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import *

urlpatterns = [
    # Aplication
    path('', TaskList.as_view(), name='task_list'),
    path('create_task/', CreateTask.as_view(), name='create_task'),
    path('delete_task/<int:pk>/', TaskFunction.delete_task, name='delete_task'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', Register.as_view(), name='register'),
    path('check_complete/<int:pk>/', TaskFunction.check_complete, name='check_complete'),
    # API
    path('account/register/', UserCreate.as_view()),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('auth/login/', LoginViewApi.as_view(), name='auth_login'),
    path('auth/logout/', LogoutViewApi.as_view(), name='auth_logout'),
    path('item_list/', ItemList.as_view(), name='item_list'),
    path('create_item/', CreateItem.as_view(), name='create_item'),
    path('delete_item/<int:pk>/', DeleteItem.as_view(), name='delete_item'),
    path('check_uncheck_complete/<int:pk>/', CheckUncheckComplete.as_view(), name='check_uncheck_complete'),
]
