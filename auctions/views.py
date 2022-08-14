import re
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import Listing, User, Bid, Comment
from django.contrib.auth.decorators import login_required
from django import forms
from .utils import usd
from django.contrib import messages


class NewForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class':'form-control'}))
    discription = forms.CharField(label="Discription", max_length=500, widget=forms.Textarea(attrs={'class':'form-control','rows': 4, 'cols': 40}))
    starting_bid = forms.FloatField(label="Starting Bid", widget=forms.NumberInput(attrs={'class': ' form-control'}), min_value=1)
    image_url = forms.CharField(label="Image URL(optional)", widget=forms.URLInput(attrs={'class':'form-control'}), required=False)
    category = forms.CharField(label="Category(optional)", widget=forms.TextInput(attrs={'class':'form-control'}), required=False)


class BidForm(forms.Form):
    bid = forms.FloatField(label="Bid", widget=forms.NumberInput(attrs={'class': ' form-control'}), min_value=1)
    
    

class AuctionStatus(forms.Form):
    status = forms.CharField(label="End Auction", widget=forms.CheckboxInput())


class CommentForm(forms.Form):
    comment = forms.CharField(label="comment",widget=forms.Textarea(attrs={'class':'form-control', 'rows': 2, 'cols': 40}), max_length=200)
    

def index(request):
    """ View all listings, default route """
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


def login_view(request):
    """ login user """
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return render(request, "auctions/login.html")
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    """ logout user form site """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """ register new user """
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Password Must Match")
            return render(request, "auctions/register.html")
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken")
            return render(request, "auctions/register.html")
        
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="login")
def create(request):
    """ create new listings """
    current_user = User.objects.get(username=request.user)
    # clean submitted data
    if request.method == "GET":
        return render(request, "auctions/createlisting.html", {
            "form": NewForm()
        })

    if request.method == "POST":
        form = NewForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Fields Empty and/or Not Valid")
            return render(request, "auctions/createlisting.html",{
                "form": NewForm(request.POST),
            })
        title = form.cleaned_data['title']
        discription = form.cleaned_data['discription']
        offer = float(form.cleaned_data['starting_bid'])
        image_url = form.cleaned_data['image_url']
        category = form.cleaned_data['category']
        if  not image_url:
            # default image 
            image_url = "https://www.shoshinsha-design.com/wp-content/uploads/2020/05/noimage-760x460.png"
        if not category:
            # default category
            category = "other"
        listing = Listing(title=title, discription=discription, offer=offer, url=image_url, category=category, author=current_user)
        listing.save()           
        return redirect("index")


@login_required(login_url="login")
def listing_item(request, id_listing):
    """ view particular listing to user """
    listing = Listing.objects.get(id=id_listing)
    current_user = User.objects.get(username=request.user)
    comments = Comment.objects.filter(listing=listing).order_by('created')
    
    # new bid form or ending auction form
    if request.method == "GET":       
        # this is for the bidder
        if not Bid.objects.filter(listing=listing, bidder=current_user).exists():
            return render(request, "auctions/listitem.html", {
                        "listing": listing, 
                        "form": BidForm(),
                        "commentForm": CommentForm(),
                        "endform": AuctionStatus(),
                        "comments_list": comments,
                    })
        else:
            # bid already placed
            return render(request, "auctions/listitem.html", {
                        "listing": listing,
                        "commentForm": CommentForm(),
                        "comments_list": comments,
                    })


@login_required(login_url="login")
def end_auction(request, id_listing):
    """ Ends auction """
    listing = Listing.objects.get(id=id_listing)
    current_user = User.objects.get(username=request.user)
    if request.method == "POST":
        if current_user == listing.author:
            # validate author's form 
            form_data = AuctionStatus(request.POST)
            if form_data.is_valid():
                if form_data.cleaned_data['status']:
                    # end auction
                    listing.status = False
                    winner = listing.winner_user()
                    if winner:
                        listing.winner = User.objects.get(id=winner)
                        listing.save()
                    return redirect("listitem", listing.id)


@login_required(login_url="login")
def bid(request, id_listing):
    listing = Listing.objects.get(id=id_listing)
    current_user = User.objects.get(username=request.user)
    bids = Bid.objects.filter(listing=listing)

    if request.method == "POST":
        # validate and update user's bid's
        bid_form_data = BidForm(request.POST)
        if bid_form_data.is_valid():
            # compare with current price
            if float(bid_form_data.cleaned_data['bid']) > listing.current_price():
                bid = Bid(bidder=current_user, bid=float(bid_form_data.cleaned_data['bid']), listing=listing)
                bid.save()
                messages.success(request, "Bid Placed")
                return render(request, "auctions/listitem.html", {
                    "listing": listing,
                    "bids": bids
                })
            else:
                # error
                messages.error(request, "Amount Should Be Higher Than Current Bid")
                return render(request, "auctions/listitem.html", {
                    "listing": listing,
                    "form": BidForm(request.POST),
                    "bids": bids
                })


@login_required(login_url="login")
def comment(request, id_listing):
    user = User.objects.get(username=request.user)
    listing = Listing.objects.get(id=id_listing)
    if request.method == "POST":
        form_data = CommentForm(request.POST)
        if form_data.is_valid():
            comment = form_data.cleaned_data["comment"]
            comments_model = Comment(author=user, listing=listing, comment=comment)
            comments_model.save()
            return redirect("listitem", listing.id)
        messages.error(request, "Failed to Post comment") 
        return render(request, "auctions/listitem.html", {
            "listing": listing,
            "commentForm": CommentForm(request.POST),
        })


@login_required(login_url="login")
def watch_list(request, id_listing=''):
    """ add to watch list and shows users watch list """
    user = User.objects.get(username=request.user)
    
    if request.method == "GET":
        watch_list = Listing.objects.all().filter(watch_list=user)
        return render(request, "auctions/watchlist.html", {
            "watchList": watch_list
        })

    if request.method == "POST":
        listing = Listing.objects.get(id=id_listing)
        # add user to listing's watch lists
        if Listing.objects.filter(id=id_listing).exists() and not listing in user.onlooker.all():
            listing.save()
            listing.watch_list.add(user)
            return redirect("listitem", id_listing)
        else:
            messages.error(request, "Could not add")
            return redirect("listitem", id_listing)


def categories(request):
    """show categories"""
    listings = Listing.objects.order_by('category').values('category').distinct()
    if request.method == "GET":
        return render(request, "auctions/categories.html", {
            "listings": listings,
        })


def category(request, category):
    """ show user selected category """
    if category:
        if Listing.objects.all().filter(category=category).exists():
            listing = Listing.objects.all().filter(category=category)
            return render(request, "auctions/index.html", {
                "listings": listing
            })
        else:
            messages.error(request, "Category doesn't exists")
            return render(request, "auctions/index.html")
    else:
        return redirect("caregories")


def remove_watchlist(request, id_listing):
    """ remove listing from user's watchlist """ 
    user = User.objects.get(username=request.user)
    try:
        listing = Listing.objects.get(id=id_listing)
    except:
        listing = None
    if request.method == "POST":
        if listing in user.onlooker.all():
            listing.watch_list.remove(user)
            return redirect("listitem", id_listing)
        else:
            messages.error(request, "No Listing")
            return redirect("index")