from django.contrib import admin

from .models import User, Comment, Bid, Listing

admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Bid)
admin.site.register(Listing)


