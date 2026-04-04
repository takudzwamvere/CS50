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
    # get all the active listings
    listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {"listings": listings})


@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            # set starting price as current price
            listing.current_price = form.cleaned_data['starting_bid']
            listing.save()
            messages.success(request, "Listing created!")
            return HttpResponseRedirect(reverse("listing_detail", args=[listing.pk]))
    else:
        form = ListingForm()

    return render(request, "auctions/create_listing.html", {"form": form})


def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    bid_form = BidForm()
    comment_form = CommentForm()
    comments = listing.comments.all()
    bid_count = listing.bids.count()

    # check if listing is on users watchlist
    on_watchlist = False
    if request.user.is_authenticated:
        if listing in request.user.watchlist.all():
            on_watchlist = True

    is_winner = False
    if not listing.is_active and request.user.is_authenticated:
        if listing.winner == request.user:
            is_winner = True

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

    # make sure auction is still going
    if not listing.is_active:
        messages.error(request, "This auction is already closed.")
        return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

    form = BidForm(request.POST)
    if form.is_valid():
        amount = form.cleaned_data['amount']

        # bid cant be less than starting bid
        if amount < listing.starting_bid:
            messages.error(request, "Bid must be at least $" + str(listing.starting_bid) + ".")
            return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

        # if there are bids already it must be higher than current
        all_bids = listing.bids.all()
        if len(all_bids) > 0:
            if amount <= listing.current_price:
                messages.error(request, "Bid must be more than the current price of $" + str(listing.current_price) + ".")
                return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

        # save the bid
        bid = Bid()
        bid.listing = listing
        bid.user = request.user
        bid.amount = amount
        bid.save()

        listing.current_price = amount
        listing.save()

        messages.success(request, "Your bid of $" + str(amount) + " was placed!")

    else:
        messages.error(request, "Something went wrong with your bid.")

    return HttpResponseRedirect(reverse("listing_detail", args=[pk]))


@login_required
def close_auction(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if request.method != "POST":
        return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

    # only the person who made the listing can close it
    if request.user != listing.created_by:
        messages.error(request, "You cant close this listing.")
        return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

    # find who bid the most
    all_bids = listing.bids.all()
    highest = None
    for b in all_bids:
        if highest is None or b.amount > highest.amount:
            highest = b

    listing.is_active = False

    if highest is not None:
        listing.winner = highest.user

    listing.save()

    if listing.winner:
        messages.success(request, "Auction closed! Winner is " + listing.winner.username + ".")
    else:
        messages.success(request, "Auction closed with no bids.")

    return HttpResponseRedirect(reverse("listing_detail", args=[pk]))


@login_required
def toggle_watchlist(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if request.method != "POST":
        return HttpResponseRedirect(reverse("listing_detail", args=[pk]))

    # check if already on watchlist and toggle it
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

    listings = profile_user.listings.all()
    bids = profile_user.bids.all()
    comments = profile_user.comments.all()
    watchlist = profile_user.watchlist.all()
    wins = profile_user.won_listings.all()

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
    # get a list of all the different categories being used
    all_cats = []
    all_listings = Listing.objects.filter(is_active=True)
    for listing in all_listings:
        if listing.category != '' and listing.category not in all_cats:
            all_cats.append(listing.category)

    all_cats.sort()

    return render(request, "auctions/categories.html", {"categories": all_cats})


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

        # make sure passwords match
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
