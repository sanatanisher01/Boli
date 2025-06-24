from django.contrib import admin
from .models import Product, Bid, UserProfile

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'base_price', 'current_highest_bid', 'end_time', 'is_active']
    list_filter = ['is_active', 'created_at', 'end_time']
    search_fields = ['title', 'description']

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['product', 'bidder', 'amount', 'timestamp']
    list_filter = ['timestamp', 'product']
    search_fields = ['product__title', 'bidder__username']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_email_verified', 'created_at']
    list_filter = ['is_email_verified', 'created_at']
    search_fields = ['user__username', 'user__email']