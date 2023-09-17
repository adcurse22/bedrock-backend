from django.urls import path
from . import views

urlpatterns = [
    path('api/register/', views.user_registration, name='user-registration'),
]
