from django.urls import path
from . import views
from django.urls import path, re_path

urlpatterns = [
    path('customer/signin/', views.customer_signin, name='home-customer_signin'),
    path('customer/signup/', views.customer_signup, name='home-customer_signup'),
    path('customer/logout/', views.home_logout_view, name='home-logout_view'),
    path('customer/profile/', views.customer_profile, name='home-customer_profile'),
    path('customer/profile/update/', views.customer_profile_update, name='home-customer_profile_update'),
    path('customer/password/change/', views.customer_password_change, name='home-customer_password_change'),
    path('customer/forgot-password/', views.forgot_password, name='home-forgot_password'),
    path('customer/verify-otp/', views.verify_otp, name='home-verify_otp'),
    path('customer/reset-password/', views.reset_password, name='home-reset_password'),

    path('charts/', views.home_page, name='home-charts'),
    path('blog/', views.home_page, name='home-blog'),
    #path('request-quote/', views.home_page, name='home-request_quote'),
    #path('projects/', views.about_page, name='home-projects'),

    # Quick Links
    path('', views.home_page, name='home-page'),  
    path('about/', views.about_page, name='home-about'),
    path('resources/', views.resources_page, name='home-resources'),
    path('news/', views.news_page, name='home-news'),

    # Company Links
    path('contact/', views.contact_page, name='home-contact'),
    path('careers/', views.careers_page, name='home-careers'),
    
    


    #JobApplication -ContactUs-NewsLetter
    path('careers/submit/', views.submit_application, name='submit_application'),
    path('contact/submit/', views.submit_contact, name='submit_contact'),
    path('newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
   
    path('partners/', views.partners_page, name='home-partners'),
    path('support/', views.support_page, name='home-support'),
    path('privacy/', views.policy_page, name='home-privacy'),
    path('terms/', views.terms_page, name='home-terms'),
    path('e-guides/', views.guide_page, name='home-e_books'),

    path('projects/', views.about_page, name='home-projects'),
    # path('projects/<int:pk>/', views.project_detail, name='home-project_detail'),
    path('projects/<slug:slug>/', views.project_detail, name='home-project_detail'),

    
    path('blog/<slug:slug>/', views.blog_detail, name='home-blog_detail'),

    path('news/<slug:slug>/', views.news_detail, name='home-news_detail'),

    path('request-quote/', views.request_quote, name='home-request_quote'),
    path('submit-enquiry/', views.submit_customer_enquiry, name='submit_customer_enquiry'),
    path('submit-question/',  views.submit_question, name='submit_question'),
    path('partner-application/', views.partner_application, name='partner_application'),



    path('partners/map/', views.partners_page_map, name='home-partners_map'),



        # list urls --------------------------------------------------------------

    path("lists/", views.home_list, name="home_list"),
    path("lists/<int:list_id>/", views.list_items, name="list_items"),
    path("lists/create/", views.create_list, name="create_list"),
    path("lists/edit/", views.edit_list, name="edit_list"),
    path("lists/delete/", views.delete_list, name="delete_list"),
    path("lists/add-to-list/", views.add_to_list, name="add_to_list"),
    path("lists/get-user-lists/", views.get_user_lists, name="get_user_lists"),
    path("lists/update-item-quantity/", views.update_item_quantity, name="update_item_quantity"),
    path("lists/delete-selected-items/", views.delete_selected_items, name="delete_selected_items"),
    path("lists/request-for-quote/<int:list_id>/", views.request_for_quote, name="request_for_quote"),
    path("lists/export-to-excel/<int:list_id>/", views.export_to_excel, name="export_to_excel"),
    path("lists/download-specifications/<int:list_id>/", views.download_specifications, name="download_specifications"),
    path("lists/download-product-list/<int:list_id>/", views.download_product_list, name="download_product_list"),
    path("lists/duplicate/<int:list_id>/", views.duplicate_list, name="duplicate_list"),
    path("lists/share/<int:list_id>/", views.share_list, name="share_list"),
    path("lists/make-default/<int:list_id>/", views.make_default_list, name="make_default_list"),

    path("lists/add-to-list/datasheet", views.add_to_list_datasheet, name="add_to_list_datasheet"),

    path('get-active-list-count/', views.get_active_list_count, name='get_active_list_count'),
    
    path('products/latest/', views.latest_products_view, name='user_account-latest_products'),
    path('products/featured/', views.featured_products_view, name='user_account-featured_products'),

    path('optimized_search/', views.optimized_search, name='optimized_search'),

    
    #path('category/<int:category_id>/', views.category_view, name='user_account-category_view'),
    path('category/<int:category_id>/', views.category_by_id, name='user_account-category_by_id'),
    path('<slug:category_slug>/', views.category_view, name='user_account-category_view'),
    path('product-list/<slug:category_slug>/', views.product_list_view, name='user_account-product_list_view'), 
    path('<slug:category_slug>/<slug:product_slug>/', views.product_detail_view, name='user_account-product_detail_view'),

    # re_path(r'^(?P<php_filename>[\w-]+\.php)$', views.php_to_category_redirect),
    re_path(r'^(?P<php_filename>[\w-]+\.php)$', views.php_to_new_url_redirect),
]
