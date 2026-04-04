from django.contrib import admin
from .models import User, Listing, Bid, Comment


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'current_price', 'category', 'is_active', 'winner', 'created_at']
    list_filter = ['is_active', 'category']
    search_fields = ['title', 'description', 'created_by__username']
    list_editable = ['is_active']


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['listing', 'user', 'amount', 'timestamp']
    list_filter = ['listing']
    search_fields = ['user__username', 'listing__title']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['listing', 'user', 'content', 'timestamp']
    search_fields = ['user__username', 'listing__title', 'content']
