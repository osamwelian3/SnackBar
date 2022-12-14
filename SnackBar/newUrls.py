from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.conf import settings as global_settings
from django.conf.urls.static import static

urlpatterns = [
    re_path(r'^.*', TemplateView.as_view(template_name='index.html'))
] + static(global_settings.MEDIA_URL, document_root=global_settings.MEDIA_ROOT)

