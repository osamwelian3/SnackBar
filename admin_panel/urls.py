from django.urls import include, path, re_path
from . import views
from SnackBar import settings
from django.conf import settings as global_settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('seller/register/', views.add_product, name='register'),
    path('add/product/', views.add_product, name='add_product'),
    path('add/category/', views.add_category, name='add_category'),
    path('products', views.my_products, name='my_products')
] + static(global_settings.MEDIA_URL, document_root=global_settings.MEDIA_ROOT) + static('/assets/', document_root=settings.ASSETS_ROOT)