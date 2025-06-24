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
    
    # OmniDimension API endpoints
    path('api/active-auctions/', views.api_active_auctions, name='api_active_auctions'),
    path('api/product/<int:pk>/status/', views.api_product_status, name='api_product_status'),
    path('api/product/<int:pk>/time-remaining/', views.api_time_remaining, name='api_time_remaining'),
    path('api/product/<int:pk>/bid-history/', views.api_bid_history, name='api_bid_history'),
    path('api/search-product/', views.api_search_product, name='api_search_product'),
    path('api/omnidimension-webhook/', views.omnidimension_webhook, name='omnidimension_webhook'),
    
    # OmniDimension Voice Agent APIs
    path('api/voice/navigate/', views.voice_navigate, name='voice_navigate'),
    path('api/voice/authenticate/', views.voice_authenticate, name='voice_authenticate'),
    path('api/voice/product-search/', views.voice_product_search, name='voice_product_search'),
    path('api/voice/place-bid/', views.voice_place_bid, name='voice_place_bid'),
    path('api/voice/get-bid-info/', views.voice_get_bid_info, name='voice_get_bid_info'),
    path('api/voice/admin-action/', views.voice_admin_action, name='voice_admin_action'),
    path('api/voice/form-action/', views.voice_form_action, name='voice_form_action'),
    path('api/voice/theme-toggle/', views.voice_theme_toggle, name='voice_theme_toggle'),
    path('api/voice/help/', views.voice_help, name='voice_help'),
]