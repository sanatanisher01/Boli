from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/bid/', views.place_bid, name='place_bid'),
    path('product/<int:pk>/current-bid/', views.get_current_bid, name='get_current_bid'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('generate-report/', views.generate_report, name='generate_report'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('email-sent/', views.email_sent, name='email_sent'),
    path('profile/', views.profile, name='profile'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uuid:token>/', views.reset_password, name='reset_password'),
    path('password-change/', auth_views.PasswordChangeView.as_view(success_url='/profile/'), name='password_change'),
    

]