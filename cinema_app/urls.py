# Đường dẫn: cinema_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('schedule/<int:showtime_id>/booking/', views.booking_view, name='booking'),
    
    path('booking/payment-return/', views.payment_return_view, name='payment_return'),
    path('booking/cancel/<str:booking_code>/', views.cancel_booking_view, name='cancel_booking'),
    path('booking/retry/<str:booking_code>/', views.retry_payment_view, name='retry_payment'),

    path('my-tickets/', views.my_tickets, name='my_tickets'),

    path('api/lock-seat/', views.lock_seat, name='api_lock_seat'),
    path('api/release-seat/', views.release_seat, name='api_release_seat'),

    # --- ĐẶT ĐỒ ĂN (MỚI) ---
    path('food/menu/', views.food_menu, name='food_menu'),
    path('food/cart/', views.view_food_cart, name='view_food_cart'),
    path('food/checkout/', views.checkout_food, name='checkout_food'),
    path('my-food-orders/', views.my_food_orders, name='my_food_orders'),
    
    path('api/add-to-food-cart/', views.add_to_food_cart, name='api_add_to_food_cart'),
    path('api/remove-food-from-cart/', views.remove_food_from_cart, name='api_remove_food_from_cart'),
    # ----------------------

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('account/', views.account_view, name='account'),

    # Manage
    path('manage/', views.manage_dashboard, name='manage_dashboard'),
    
    # --- THÊM DÒNG NÀY ---
    path('manage/analytics/', views.manage_analytics, name='manage_analytics'),
    # ---------------------

    path('manage/movies/', views.manage_movies, name='manage_movies'),
    path('manage/movies/create/', views.manage_movie_create, name='manage_movie_create'),
    path('manage/movies/<int:pk>/edit/', views.manage_movie_edit, name='manage_movie_edit'),
    path('manage/movies/<int:pk>/delete/', views.manage_movie_delete, name='manage_movie_delete'),
    
    path('manage/rooms/', views.manage_rooms, name='manage_rooms'),
    path('manage/rooms/create/', views.manage_room_create, name='manage_room_create'),
    path('manage/rooms/<int:pk>/edit/', views.manage_room_edit, name='manage_room_edit'),
    path('manage/rooms/<int:pk>/delete/', views.manage_room_delete, name='manage_room_delete'),
    
    path('manage/showtimes/', views.manage_showtimes, name='manage_showtimes'),
    path('manage/showtimes/create/', views.manage_showtime_create, name='manage_showtime_create'),
    path('manage/showtimes/<int:pk>/edit/', views.manage_showtime_edit, name='manage_showtime_edit'),
    path('manage/showtimes/<int:pk>/delete/', views.manage_showtime_delete, name='manage_showtime_delete'),
    
    path('manage/promotions/', views.manage_promotions, name='manage_promotions'),
    path('manage/promotions/create/', views.manage_promotion_create, name='manage_promotion_create'),
    path('manage/promotions/<int:pk>/edit/', views.manage_promotion_edit, name='manage_promotion_edit'),
    path('manage/promotions/<int:pk>/delete/', views.manage_promotion_delete, name='manage_promotion_delete'),
    
    path('manage/reports/', views.manage_reports, name='manage_reports'),


    
    # --- QUẢN LÝ NGƯỜI DÙNG (MỚI) ---
    path('manage/users/', views.manage_users, name='manage_users'),
    path('manage/users/create/', views.manage_user_create, name='manage_user_create'),
    path('manage/users/<int:pk>/edit/', views.manage_user_edit, name='manage_user_edit'),
    path('manage/users/<int:pk>/delete/', views.manage_user_delete, name='manage_user_delete'),
    # --------------------------------

    # --- QUẢN LÝ ĐỒ ĂN (MỚI) ---
    path('manage/foods/', views.manage_foods, name='manage_foods'),
    path('manage/foods/create/', views.manage_food_create, name='manage_food_create'),
    path('manage/foods/<int:pk>/edit/', views.manage_food_edit, name='manage_food_edit'),
    path('manage/foods/<int:pk>/delete/', views.manage_food_delete, name='manage_food_delete'),
    path('manage/food-orders/', views.manage_food_orders, name='manage_food_orders'),
    # --------------------------------

]