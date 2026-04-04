from django.urls import path
from . import views

urlpatterns = [
    # Default route – active listings
    path("", views.index, name="index"),

    # Authentication & Profile
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>/", views.profile_view, name="profile"),

    # Listings
    path("create/", views.create_listing, name="create_listing"),
    path("listing/<int:pk>/", views.listing_detail, name="listing_detail"),
    path("listing/<int:pk>/bid/", views.place_bid, name="place_bid"),
    path("listing/<int:pk>/close/", views.close_auction, name="close_auction"),
    path("listing/<int:pk>/watchlist/", views.toggle_watchlist, name="toggle_watchlist"),
    path("listing/<int:pk>/comment/", views.add_comment, name="add_comment"),

    # Watchlist
    path("watchlist/", views.watchlist_view, name="watchlist"),

    # Categories
    path("categories/", views.categories, name="categories"),
    path("categories/<str:name>/", views.category_listings, name="category_listings"),
]
