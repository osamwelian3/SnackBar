from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^product/$', views.product_index, {}, name='product_index'),
    re_path(r'^category/$', views.category_index, {}, name='category_index'),
    re_path(r'^category/(?P<category_slug>[-\w]+)/$', views.show_category, name='catalog_category'),
    re_path(r'^product/(?P<product_slug>[-\w]+)/$', views.show_product, name='catalog_product'),
    re_path(r'^test_upload/$', views.test_upload, {}),
    re_path(r'^delete/(?P<filename>[-\w]+)/$', views.delete_image, name='delete'),
]
