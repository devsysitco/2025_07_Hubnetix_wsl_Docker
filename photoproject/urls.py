"""
URL configuration for django_hubnetix project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    #path('summernote/', include('django_summernote.urls')),
    path('account/',include('user_account.urls')),
    path('manager/', include('admin_dashboard.urls')),
    path('seo-manager/', include('seo_dashboard.urls')),
    path('partner-manager/', include('partner_dashboard.urls')),
    path('',include('home.urls')),

]

handler404 = 'home.views.error_404'

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

# Only use this for local development (not production)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('gallery.urls')),  # root page
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
