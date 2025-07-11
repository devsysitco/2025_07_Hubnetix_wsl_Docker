from django.urls import path
from . import views
from catalog.views import (
                category_list, category_create, category_edit, category_details, category_delete,
                product_list, product_create, product_details, product_edit, product_delete,
                download_document,view_document,datasheet_list,datasheet_create,datasheet_edit,datasheet_details,datasheet_delete
                )


urlpatterns = [
    path('', views.dashboard_view, name='admin_dashboard-dashboard'),
    path('logout/', views.dashboard_logout, name="admin_dashboard-logout"),
    path('categories/', category_list, name='admin_dashboard-category_list'),
    path('categories/add/', category_create, name='admin_dashboard-category_add'),
    path('categories/<int:pk>/edit/', category_edit, name='admin_dashboard-category_edit'),
    path('categories/<int:pk>/', category_details, name='admin_dashboard-category_details'),
    path('categories/<int:pk>/delete/', category_delete, name='admin_dashboard-category_delete'),

    path('products/', product_list, name='admin_dashboard-products_list'),
    path('products/add/', product_create, name='admin_dashboard-product_add'),
    path('products/<int:pk>/', product_details, name='admin_dashboard-product_details'),
    path('products/<int:pk>/edit/', product_edit, name='admin_dashboard-product_edit'),
    path('product/delete/<int:pk>/', product_delete, name='admin_dashboard-product_delete'),
   

    path('document/<int:doc_id>/download/', download_document, name='admin_dashboard-download_document'),
    path('view-document/<int:doc_id>/', view_document, name='admin_dashboard-view_document'),

    path('news_article/', views.news_article_list, name='admin_dashboard-news_article_list'),
    path('news_article/add/', views.news_article_create, name='admin_dashboard-news_article_create'),
    path('news_article/<int:pk>/edit/', views.news_article_edit, name='admin_dashboard-news_article_edit'),
    path('news_article/<int:pk>/',views.news_article_details, name='admin_dashboard-news_article_details'),
    path('news_article/delete/<int:pk>/',views.news_article_delete, name='admin_dashboard-news_article_delete'),


    path('blog_post/', views.blog_post_list, name='admin_dashboard-blog_post_list'),
    path('blog_post/add/', views.blog_post_create, name='admin_dashboard-blog_post_create'),
    path('blog_post/<int:pk>/edit/', views.blog_post_edit, name='admin_dashboard-blog_post_edit'),
    path('blog_post/<int:pk>/',views.blog_post_details, name='admin_dashboard-blog_post_details'),
    path('blog_post/delete/<int:pk>/',views.blog_post_delete, name='admin_dashboard-blog_post_delete'),


    path('job_listing/', views.job_listing_list, name='admin_dashboard-job_listing_list'),
    path('job_listing/add/', views.job_listing_create, name='admin_dashboard-job_listing_create'),
    path('job_listing/<int:pk>/edit/', views.job_listing_edit, name='admin_dashboard-job_listing_edit'),
    path('job_listing/<int:pk>/', views.job_listing_details, name='admin_dashboard-job_listing_details'),
    path('job_listing/delete/<int:pk>/', views.job_listing_delete, name='admin_dashboard-job_listing_delete'),

    path('projects/', views.project_list, name='admin_dashboard-project_list'),
    path('projects/add/', views.project_create, name='admin_dashboard-project_create'),
    path('projects/<int:pk>/edit/', views.project_edit, name='admin_dashboard-project_edit'),
    path('projects/<int:pk>/', views.project_details, name='admin_dashboard-project_details'),
    path('projects/delete/<int:pk>/', views.project_delete, name='admin_dashboard-project_delete'),
    

    
    path('job-applications/', views.job_application_list, name='admin_dashboard-job_application_list'),
    path('job-applications/<int:pk>/', views.job_application_details, name='admin_dashboard-job_application_details'),
    path('job-applications/delete/<int:pk>/', views.job_application_delete, name='admin_dashboard-job_application_delete'),
    
    
    path('contact-submissions/', views.contact_submission_list, name='admin_dashboard-contact_submission_list'),
    path('contact-submissions/<int:pk>/', views.contact_submission_details, name='admin_dashboard-contact_submission_detail'),
    path('contact-submissions/delete/<int:pk>/', views.contact_submission_delete, name='admin_dashboard-contact_submission_delete'),
    
    
    path('newsletter-subscriptions/', views.newsletter_subscription_list, name='admin_dashboard-newsletter_subscription_list'),
    path('newsletter-subscriptions/delete/<int:pk>/', views.newsletter_subscription_delete, name='admin_dashboard-newsletter_subscription_delete'),
    path('newsletter-subscriptions/toggle-status/', views.newsletter_subscription_toggle_status, name='admin_dashboard-newsletter_subscription_toggle_status'),

    path('fill-all-fields/', views.fill_all_models_fields, name='admin_dashboard-fill_all_model_fields'),

    path('partner/', views.partner_list, name='admin_dashboard-partner_list'),
    path('partner/add/', views.partner_create, name='admin_dashboard-partner_create'),
    path('partner/<int:pk>/edit/', views.partner_edit, name='admin_dashboard-partner_edit'),
    path('partner/<int:pk>/', views.partner_details, name='admin_dashboard-partner_details'),
    path('partner/delete/<int:pk>/', views.partner_delete, name='admin_dashboard-partner_delete'),


    path('resources/', views.resource_list, name='admin_dashboard-resource_list'),
    path('resources/create/', views.resource_create, name='admin_dashboard-resource_create'),
    path('resources/<int:pk>/', views.resource_details, name='admin_dashboard-resource_details'),
    path('resources/<int:pk>/download/', views.download_resource, name='admin_dashboard-resource_download'),
    path('resources/<int:pk>/edit/', views.resource_edit, name='admin_dashboard-resource_edit'),
    path('resources/<int:pk>/delete/', views.resource_delete, name='admin_dashboard-resource_delete'),


    path('datasheet/', datasheet_list, name='admin_dashboard-datasheet_list'),
    path('datasheet/add/', datasheet_create, name='admin_dashboard-datasheet_create'),
    path('datasheet/<int:pk>/edit/', datasheet_edit, name='admin_dashboard-datasheet_edit'),
    path('datasheet/<int:pk>/', datasheet_details, name='admin_dashboard-datasheet_details'),
    path('datasheet/delete/<int:pk>/', datasheet_delete, name='admin_dashboard-datasheet_delete'),

    # Banner URLs
    path('banner/', views.banner_list, name='admin_dashboard-banner_list'),
    path('banner/add/', views.banner_create, name='admin_dashboard-banner_create'),
    path('banner/<int:pk>/edit/', views.banner_edit, name='admin_dashboard-banner_edit'),
    path('banner/<int:pk>/', views.banner_details, name='admin_dashboard-banner_details'),
    path('banner/delete/<int:pk>/', views.banner_delete, name='admin_dashboard-banner_delete'),

    # Office Location URLs
    path('office-location/', views.office_location_list, name='admin_dashboard-office_location_list'),
    path('office-location/add/', views.office_location_create, name='admin_dashboard-office_location_create'),
    path('office-location/<int:pk>/edit/', views.office_location_edit, name='admin_dashboard-office_location_edit'),
    path('office-location/<int:pk>/', views.office_location_details, name='admin_dashboard-office_location_details'),
    path('office-location/delete/<int:pk>/', views.office_location_delete, name='admin_dashboard-office_location_delete'),
    
]















