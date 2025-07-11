from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='account-login-page'),
    path('login/', views.account_login, name='user_account-login-function'),
    path('create_admin_user/', views.create_admin_user, name='create_admin_user'),
    path('create_account_type/', views.create_account_type, name='create_partner_account_type'),
    path('check-session/', views.check_existing_session, name='check-existing-session'),
    
]