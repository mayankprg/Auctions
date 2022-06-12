
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')


class Listing(models.Model):

    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    title = models.CharField(max_length=65)
    discription = models.TextField(max_length=500)
    offer = models.FloatField(blank=False)
    url = models.URLField()
    category = models.CharField(max_length=250)
    status = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_user')
    highest = models.ForeignKey("Bid", on_delete=models.PROTECT, null=True, blank=True, related_name='bid_user')
    created = models.DateTimeField(default=timezone.now)
    watch_list = models.ManyToManyField(User, blank=True, related_name='listings')
    
    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):

    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    bid = models.FloatField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bidder')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="on_auction") 
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"userId: {self.bidder}"


class Comment(models.Model):

    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='on_listing')
    comment = models.TextField(max_length=200, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"user: {self.author}, on: {self.listing}"


