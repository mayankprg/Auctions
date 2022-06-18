
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    def watchlist_count(self):
        return self.onlooker.all().count()


class Listing(models.Model):

    title = models.CharField(max_length=65)
    discription = models.TextField(max_length=500)
    offer = models.FloatField(blank=False)
    url = models.URLField()
    category = models.CharField(max_length=250)
    status = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auction')
    created = models.DateTimeField(default=timezone.now)
    winner = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="winner")
    watch_list = models.ManyToManyField(User, blank=True, related_name='onlooker')

    def total_bids(self):
        return self.bids.all().count()

    def total_comments(self):
        return self.comment.all().count()

    def highest_bid(self):
        return self.bids.all().order_by('-bid').first().bid
        
    def current_price(self):
        if self.bids.all().exists():
            return self.highest_bid()
        else:
            return self.offer

    def winner_user(self):
        if self.current_price() > self.offer:
            return  self.bids.all().order_by('-bid').first().bidder_id
        else:
            return None

    def categories(self):
        return self.categories.all()

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):

    bid = models.FloatField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bid_amount')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids") 
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"userId: {self.bidder}"


class Comment(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comment')
    comment = models.TextField(max_length=200, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"user: {self.author}, on: {self.listing}"


