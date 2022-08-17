from django.urls import path
from . import views

urlpatterns = [
    path('update_profile/', views.update_profile),
    path('view_profile/', views.view_profile),
]