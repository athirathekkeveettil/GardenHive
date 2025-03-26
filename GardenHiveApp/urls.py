from django.urls import path
from . import views


urlpatterns=[
    path("", views.index, name="index"),
    path('login', views.login_view, name="login"), 

    path('register', views.register),
    path('nurseryRegister',views.nurseryRegister, name="nurseryRegister"),
    path('userRegister',views.userRegister, name="userRegister"),

    path('adminhome', views.adminhome),

    path('admin_manage_accounts/', views.admin_manage_accounts, name="admin_manage_accounts"),
    path('admin_manage_accounts/delete/<int:user_id>/', views.delete_user, name="delete_user"),
    path('admin_manage_accounts/delete/<int:nursery_id>/', views.delete_nursery, name="delete_nursery"),

    path('admin_category', views.admin_category, name="admin_category"),
    path('admin_category/update/<int:category_id>/', views.update_category, name="update_category"),
    path('admin_category/delete/<int:category_id>/', views.delete_category, name="delete_category"),

    path('admin_subcategory/', views.admin_subcategory, name='admin_subcategory'),
    path('subcategory/update/<int:subcategory_id>/', views.update_subcategory, name='update_subcategory'),
    path('subcategory/delete/<int:subcategory_id>/', views.delete_subcategory, name='delete_subcategory'),

    path('admin_care_tips/', views.admin_care_tips, name="admin_care_tips"),  
    path('admin_care_tips/update/<int:care_tip_id>/', views.update_care_tip, name="update_care_tip"), 
    path('admin_care_tips/delete/<int:care_tip_id>/', views.delete_care_tip, name="delete_care_tip"),  

    path('adminapprovenursery', views.adminapprovenursery, name="adminapprovenursery"),
    path("adminapprovenursery/approve/<int:nursery_id>/", views.approve_nursery, name="approve_nursery"),
    path("adminapprovenursery/reject/<int:nursery_id>/", views.reject_nursery, name="reject_nursery"),
    
    path('nurseryhome', views.nurseryhome, name="nurseryhome"),
    path('add_staff/', views.add_staff, name='add_staff'),
    path('nursery/<int:nursery_id>/add_staff/', views.add_staff, name='add_staff'),
    path('nursery/<int:nursery_id>/staff_list/', views.staff_list, name='staff_list'),
    path('nursery/<int:nursery_id>/edit_staff/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    path('nursery/<int:nursery_id>/delete_staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('staff_list/', views.staff_list, name='staff_list_all'),
    path('my_products/', views.product_list, name='product_list'),
    path('product_list/', views.product_list, name='product_list'), 
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),

    path('nursery_products/', views.nursery_products, name='nursery_products'),
    path('nursery/<int:nursery_id>/bookings/', views.nursery_bookings, name='nursery_bookings'),
 
    path("userhome/", views.userhome, name="userhome"),
    path('cart/', views.cart_view, name='cart'),

    path('checkout/', views.checkout_view, name='checkout'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('book/', views.book_cart, name='book_cart'), 
    path('booking_success/', views.booking_success, name='booking_success'),

    path('book_from_cart/', views.book_from_cart, name='book_from_cart'),
    path('user_bookings/', views.user_bookings, name='user_bookings'),
    
    path('bookings/', views.view_bookings, name='view_booking'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    path('proceed_to_booking/', views.proceed_to_booking, name='proceed_to_booking'),
    path('confirm_booking/', views.confirm_booking, name='confirm_booking'),
    
    path('payment/<int:total_price>/', views.payment, name='payment'),
    path('payment_success/', views.payment_success, name='payment_success'),

    path("care_tips/", views.care_tips, name="care_tips"),
    path("products/", views.product_search, name="product_search"),
    path("search_nursery/", views.search_nursery, name="search_nursery"),

    path("search/", views.search_products, name="search_products"),
    path("image_search/", views.image_search, name="image_search"),
    
    path('about', views.about),

    path('service', views.service),
]
