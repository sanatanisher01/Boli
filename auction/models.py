from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cloudinary.models import CloudinaryField
import uuid

class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = CloudinaryField('image', folder='products/')
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def current_highest_bid(self):
        highest_bid = self.bids.order_by('-amount').first()
        return highest_bid.amount if highest_bid else self.base_price

    @property
    def highest_bidder(self):
        highest_bid = self.bids.order_by('-amount').first()
        return highest_bid.bidder if highest_bid else None

    @property
    def is_expired(self):
        return timezone.now() > self.end_time

    @property
    def top_bidders(self):
        return self.bids.order_by('-amount')[:3]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default=False)
    activation_token = models.UUIDField(default=uuid.uuid4, editable=False)
    profile_picture = CloudinaryField('image', folder='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Verified: {self.is_email_verified}"

class Bid(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.bidder.username} - {self.amount} on {self.product.title}"