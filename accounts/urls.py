from django.urls import path
from . import views

urlpatterns = [
    path('get_csrf/', views.setCsrfCookie),
    path('register/', views.signup),
]