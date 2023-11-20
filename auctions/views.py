import re
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Category
from .forms import ListingForm, BidForm, CommentForm

from django.http import JsonResponse
import json



def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            next_url = request.POST.get("next", "index")
            return redirect(next_url)
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        next_url = request.GET.get("next", "index")
        return render(request, "auctions/login.html", {"next": next_url})


def logout_view(request):
    logout(request)
    return redirect("index")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return redirect("index")
    else:
        return render(request, "auctions/register.html")


def index(request):
    user_watched = request.user.watched_listings.order_by("-id")
    watched_ids = []
    for l in user_watched:
        watched_ids.append(l.id)
    print(watched_ids)
    return render(
        request,
        "auctions/index.html",
        {
            "listings": Listing.objects.all()
            .filter(active=True)
            .order_by("-created_at"),
            "banner": "Active Listings",
            "watched":watched_ids
        },
    )


def listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    being_watched = listing.watchers.filter(id=request.user.id).exists()
    form = CommentForm()
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        print(body)
        data = json.loads(body)
        clicked= data['doit']

        if clicked == "toggle-watcher":
            listing.toggle_watcher(request.user)
            being_watched = listing.watchers.filter(id=request.user.id).exists()
            response = {
                "success": True,
                "id":listing_id,
                "watching": being_watched
            }
            return JsonResponse(response)
        elif clicked == "bid":
            return redirect('bid', listing_id=listing.id)
            return HttpResponse("make a bid")
        elif clicked == "close-auction":
            listing.active = False
            listing.save()
            return redirect('my-listings')
        elif clicked == "add-comment":
            #return redirect('add-comment', listing_id=listing_id)
            formData = data['form']
            print(formData)
            print("sending to add comment")
            res = add_comment(request, listing_id)
            print(res)
            response = {
                "success": False,
                "id":listing_id,
                "message": "Problem of some sort"
            }
            return res
        else:
            return HttpResponseServerError(f'Unknown button clicked')
    else:
        
        return render(request, "auctions/listing.html", {
            'listing': listing,
            'being_watched': being_watched,
            'form':form
        })


@login_required(login_url="login")
def my_listings(request):
    # user.id needed because user is SimpleLazyObject, not reconstituted
    listings1 = Listing.objects.filter(creator=request.user.id).order_by("-created_at")
    listings2 = request.user.listings.all().order_by("-created_at")

    user_watched = request.user.watched_listings.order_by("-id")
    watched_ids = []
    for l in user_watched:
        watched_ids.append(l.id)

    return render(
        request,
        "auctions/index.html",
        {
            "listings": request.user.listings.order_by("-created_at"),
            "banner": "My Listings",
            "watched": watched_ids,
        },
    )


@login_required(login_url="login")
def my_watchlist(request):
    user_watched = request.user.watched_listings.order_by("-id")
    watched_ids = []
    for l in user_watched:
        watched_ids.append(l.id)

    return render(
        request,
        "auctions/index.html",
        {
            "listings": request.user.watched_listings.order_by("-created_at"),
            "banner": "My Watchlist",
            "watched": watched_ids
        },
    )


def categories(request):
    return render(
        request,
        "auctions/categories.html",
        {
            "categories": Category.objects.all().order_by("name"),
        },
    )


def category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    listings = Listing.objects.filter(categories=category, active=True)
    return render(
        request,
        "auctions/index.html",
        {
            "listings": listings,
            "banner": f"{category.name} Listings",
        },
    )


@login_required(login_url="login")
def create_listing(request):
    if request.method == "POST":
        if "cancel" in request.POST:
            return redirect("index")
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.creator = request.user
            listing.save()
            form.save_m2m()
            messages.success(request, f"Listing created successfully!")
            return redirect("index")
        else:
            messages.error(request, "Problem creating the listing. Details below.")
    else:
        form = ListingForm(initial={"starting_bid": 1})
    return render(request, "auctions/new_listing.html", {"form": form})


@login_required(login_url="login")
# possible todo: prevent user to bid on his own listing
def bid(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    if request.method == "POST":
        form = BidForm(request.POST)
        form.set_minimum_bid(listing.minimum_bid())
        if form.is_valid():
            bid = form.save(commit=False)
            bid.bidder = request.user
            bid.listing = listing
            bid.save()
            return redirect("listing", listing_id=listing_id)
        else:
            messages.error(request, "Problem with the bid")
    else:
        form = BidForm(initial={"amount": listing.minimum_bid})
    return render(
        request,
        "auctions/bid.html",
        {
            "form": form,
            "listing": listing,
        },
    )

    

@login_required(login_url="login")
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    if request.method == "POST":
        print("got to add comment")
        if "cancel" in request.POST:
            print("if cancel")
            return redirect("listing", listing_id=listing_id)
        
        body = request.body.decode('utf-8')
        print(body)
        data = json.loads(body)
        formData = data['form']

        form = CommentForm(formData)
        if form.is_valid():
            print("first if valid")
            comment = form.save(commit=False)
            comment.commentor = request.user
            comment.listing = listing
            comment.save()
            response = {
                "success": True,
                "id":listing_id,
            }
            return JsonResponse(response)
            #return redirect("listing", listing_id=listing_id)
        else:
            print('else not valid')
            #messages.error(request, "Problem creating the comment. Details below.")
            response = {
                "success": False,
                "id":listing_id,
                "message": "Problem with validation"
            }
            return JsonResponse(response)
    else:
        print('else nothing')
    #     form = CommentForm()
    # return render(
    #     request,
    #     "auctions/listing.html",
    #     {"form": form, "listing": listing, "show_CommentForm": "yes"},
    # )
        
