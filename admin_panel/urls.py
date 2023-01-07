from django.urls import include, path, re_path
from . import views
from SnackBar import settings
from django.conf import settings as global_settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('seller/register/', views.add_product, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/product/', views.add_product, name='add_product'),
    path('update/product/<slug:product_slug>', views.update_product, name='update_product'),
    path('delete/thumbnail/<slug:product_slug>/<int:pos>', views.delete_thumbnail, name='delete_thumbnail'),
    path('product/<slug:product_slug>/activate/', views.activate_product, name='activate_product'),
    path('add/category/', views.add_category, name='add_category'),
    path('products', views.my_products, name='my_products')
] + static(global_settings.MEDIA_URL, document_root=global_settings.MEDIA_ROOT) + static('/assets/', document_root=settings.ASSETS_ROOT)