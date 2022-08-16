from django.urls import path
from . import views

urlpatterns = [
    path('get_csrf/', views.setCsrfCookie),
    path('get_auth_status/', views.isAuthenticated),
    path('register/', views.signup),
    path('activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
    path('login/', views.signin),
    path('logout/', views.log_out),
]