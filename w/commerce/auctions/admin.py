from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Listing, Bid, Comment


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # add our custom fields to the default UserAdmin
    fieldsets = UserAdmin.fieldsets + (
        ('Auction Info', {'fields': ('watchlist',)}),
    )
    filter_horizontal = ('watchlist', 'groups', 'user_permissions')


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'current_price', 'is_active']


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['listing', 'user', 'amount', 'timestamp']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['listing', 'user', 'timestamp']
