from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from .models import User, Listing, Bid, Comment
from .forms import ListingForm, BidForm, CommentForm


def index(request):
    listings = Listing.objects.filter(is_active=True).order_by('-created_at')
    return render(request, "auctions/index.html", {"listings": listings})


@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            listing.current_price = form.cleaned_data['starting_bid']
            listing.save()
            messages.success(request, "Listing created successfully!")
            return HttpResponseRedirect(reverse("listing_detail", args=[listing.pk]))
    else:
        form = ListingForm()
    return render(request, "auctions/create_listing.html", {"form": form})


def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    bid_form = BidForm()
    comment_form = CommentForm()
    comments = listing.comments.all().order_by('-timestamp')
    bid_count = listing.bids.count()

    on_watchlist = request.user.is_authenticated and listing in request.user.watchlist.all()

    is_winner = (
        not listing.is_active and
        request.user.is_authenticated and
        listing.winner == request.user
    )

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid_form": bid_form,
        "comment_form": comment_form,
        "comments": comments,
        "bid_count": bid_count,
        "on_watchlist": on_watchlist,
        "is_winner": is_winner,
    })


@login_required
def place_bid(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if request.method != "POST":
        return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

    if not listing.is_active:
        messages.error(request, "This auction has already closed.")
        return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

    form = BidForm(request.POST)
    if form.is_valid():
        amount = form.cleaned_data['amount']

        # bid must be at least the starting bid
        if amount < listing.starting_bid:
            messages.error(request, f"Bid must be at least ${listing.starting_bid}.")
            return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

        # if there are already bids, new bid must be higher than current price
        if listing.bids.exists() and amount <= listing.current_price:
            messages.error(request, f"Bid must be greater than the current price of ${listing.current_price}.")
            return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

        bid = Bid(listing=listing, user=request.user, amount=amount)
        bid.save()
        listing.current_price = amount
        listing.save()
        messages.success(request, f"Bid of ${amount} placed!")
    else:
        messages.error(request, "Invalid bid.")

    return HttpResponseRedirect(reverse("listing_detail", args=[pk]))


@login_required
def close_auction(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if request.method != "POST":
        return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

    if request.user != listing.created_by:
        messages.error(request, "Only the listing creator can close this auction.")
        return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

    # find the highest bid
    highest_bid = listing.bids.order_by('-amount').first()
    listing.is_active = False
    listing.winner = highest_bid.user if highest_bid else None
    listing.save()

    if listing.winner:
        messages.success(request, f"Auction closed. Winner: {listing.winner.username}.")
    else:
        messages.success(request, "Auction closed with no bids.")

    return HttpResponseRedirect(reverse("listing_detail", args=[pk]))


@login_required
def toggle_watchlist(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if request.method != "POST":
        return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

    if listing in request.user.watchlist.all():
        request.user.watchlist.remove(listing)
        messages.info(request, "Removed from watchlist.")
    else:
        request.user.watchlist.add(listing)
        messages.info(request, "Added to watchlist.")

    return HttpResponseRedirect(reverse("listing_detail", args=[pk]))


@login_required
def watchlist_view(request):
    listings = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {"listings": listings})


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    # gather user's activity
    listings = profile_user.listings.all().order_by('-created_at')
    bids = profile_user.bids.all().order_by('-timestamp')
    comments = profile_user.comments.all().order_by('-timestamp')
    watchlist = profile_user.watchlist.all()
    wins = profile_user.won_listings.all().order_by('-created_at')
    
    return render(request, "auctions/profile.html", {
        "profile_user": profile_user,
        "listings": listings,
        "bids": bids,
        "comments": comments,
        "watchlist": watchlist,
        "wins": wins
    })


@login_required
def add_comment(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if request.method != "POST":
        return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.listing = listing
        comment.user = request.user
        comment.save()

    return HttpResponseRedirect(reverse("listing_detail", args=[pk]))


def categories(request):
    cats = (
        Listing.objects
        .filter(is_active=True)
        .exclude(category='')
        .values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )
    return render(request, "auctions/categories.html", {"categories": cats})


def category_listings(request, name):
    listings = Listing.objects.filter(is_active=True, category=name)
    return render(request, "auctions/category_listings.html", {
        "listings": listings,
        "category": name,
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
