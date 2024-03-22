from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout', views.logout, name='logout'),
    
    path('home_a', views.home_a, name='home_a'),
    path('home_u', views.home_u, name='home_u'),
    path('register/', views.register, name='register'),

    path('login', views.login, name='login'),
    path('login_view', views.login_view, name='login_view'),
    
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve_user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('disapprove_user/<int:user_id>/', views.disapprove_user, name='disapprove_user'),
    
    path('book_management', views.book_management, name='book_management'),
    path('book_management_u', views.book_management_u, name='book_management_u'),
    path('add_book/', views.add_book, name='add_book'),
    path('edit_book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('delete_book/<int:book_id>/', views.delete_book, name='delete_book'),
    
    path('view_users/', views.view_users, name='view_users'),
    path('view_user_rental_history/', views.view_user_rental_history, name='view_user_rental_history'),
    path('overdue_inform/<int:rental_id>/', views.overdue_inform, name='overdue_inform'),

    path('search_books/', views.search_books, name='search_books'),
    
    path('rent_book/', views.rent_book, name='rent_book'),
    
    path('rent_book/<int:book_id>/', views.rent_book, name='rent_book'),
    path('return_book/<int:rental_id>/', views.return_book, name='return_book'),
    path('report_lost_book/<int:rental_id>/', views.report_lost_book, name='report_lost_book'),
    path('rental_history', views.rental_history, name='rental_history'),
    
    
    
    path('add_category/', views.add_category, name='add_category'),
    path('reset_password/', views.reset_password, name='reset_password'),
    
    
    path('view_profile', views.view_profile, name='view_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
   
    path('view_cart', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('remove_from_cart/<int:book_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('purchase_books/', views.purchase_books, name='purchase_books'),
    path('checkout/', views.checkout, name='checkout'),
    
    path('unapproved-users/', views.unapproved_users, name='unapproved_users'),
    
    path('user_rentals_next_day/', views.user_rentals_next_day, name='user_rentals_next_day'),
    path('user_rentals_next_day_ad', views.user_rentals_next_day_ad, name='user_rentals_next_day_ad'),
    
    path('categories/', views.categories, name='categories'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    
    path('thankyou/<int:purchase_id>/', views.thankyou, name='thankyou'),
    path('purchase_history/', views.purchase_history, name='purchase_history'),
    
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    
    path('rental_requests/', views.rental_requests, name='rental_requests'),
    path('return_requests/', views.return_requests, name='return_requests'),
    
    path('rental_requests_admin/', views.rental_requests_admin, name='rental_requests_admin'),
    path('return_requests_admin/', views.return_requests_admin, name='return_requests_admin'),
    path('approve_rental_request/<int:rental_id>/', views.approve_rental_request, name='approve_rental_request'),
    path('approve_return_request/<int:rental_id>/', views.approve_return_request, name='approve_return_request'),


    
    
]
