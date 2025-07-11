# urls.py
from django.urls import path
from .views import cover_upload_view, preview_cover, upload_cover_api

urlpatterns = [
    path('cover/upload/', cover_upload_view, name='cover_upload'),
    path('upload/api/', upload_cover_api, name='upload_cover'),
    path('preview/', preview_cover, name='preview_cover'),
]