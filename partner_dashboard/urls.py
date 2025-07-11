from django.urls import path
from . import views
from catalog.views import category_list


urlpatterns = [
    path('', views.dashboard_view, name='partner_dashboard-dashboard'),
    path('logout/', views.dashboard_logout, name="partner_dashboard-logout"),
    path('categories/', category_list, name='partner_dashboard-category_list'),
    path('resources/', views.resource_list, name='partner_dashboard-resource_list'),
    path('resources/<int:pk>/', views.resource_details, name='partner_dashboard-resource_details'),
    path('resources/<int:pk>/download/', views.download_resource, name='partner_dashboard-resource_download'),

]















