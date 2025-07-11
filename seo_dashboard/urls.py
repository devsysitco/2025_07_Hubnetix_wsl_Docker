from django.urls import path
from . import views  # Import views from the current directory

urlpatterns = [    
    path('', views.dashboard_view, name='seo_dashboard-dashboard'),
    path('logout/', views.dashboard_logout, name="seo_dashboard-logout"),
    path('categories/', views.category_list, name='seo_dashboard-category_list'),
    path('categories/<int:pk>/edit/', views.category_edit, name='seo_dashboard-category_edit'),
    path('categories/<int:pk>/', views.category_details, name='seo_dashboard-category_details'),
    

    path('products/', views.product_list, name='seo_dashboard-products_list'),
    path('products/<int:pk>/', views.product_details, name='seo_dashboard-product_details'),
    path('products/<int:pk>/edit/', views.product_edit, name='seo_dashboard-product_edit'),

    path('news-article/', views.news_article_list, name='seo_dashboard-news_article_list'),
    path('news-article/<int:pk>/edit/', views.news_article_edit, name='seo_dashboard-news_article_edit'),
    path('news-article/<int:pk>/',views.news_article_details, name='seo_dashboard-news_article_details'),
    
    path('blog-post/', views.blog_post_list, name='seo_dashboard-blog_post_list'),
    path('blog-post/<int:pk>/edit/', views.blog_post_edit, name='seo_dashboard-blog_post_edit'),
    path('blog-post/<int:pk>/',views.blog_post_details, name='seo_dashboard-blog_post_details'),

    path('projects/', views.project_list, name='seo_dashboard-project_list'),
    path('projects/<int:pk>/edit/', views.project_edit, name='seo_dashboard-project_edit'),
    path('projects/<int:pk>/', views.project_details, name='seo_dashboard-project_details'),
    

    path('old-url-redirect/', views.old_url_redirect_list, name='seo_dashboard-old_url_redirect_list'),
    path('old-url-redirect/add/', views.old_url_redirect_create, name='seo_dashboard-old_url_redirect_create'),
    path('old-url-redirect/<int:pk>/edit/', views.old_url_redirect_edit, name='seo_dashboard-old_url_redirect_edit'),
    path('old-url-redirect/<int:pk>/', views.old_url_redirect_details, name='seo_dashboard-old_url_redirect_details'),
    path('old-url-redirect/delete/<int:pk>/', views.old_url_redirect_delete, name='seo_dashboard-old_url_redirect_delete'),

]







    

















