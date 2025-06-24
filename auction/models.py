from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cloudinary.models import CloudinaryField
import uuid
import random
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

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

def generate_unique_id():
    """Generate a random 6-digit unique ID"""
    return random.randint(100000, 999999)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default=False)
    activation_token = models.UUIDField(default=uuid.uuid4, editable=False)
    profile_picture = CloudinaryField('image', folder='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    unique_id = models.IntegerField(unique=True, null=True, blank=True)
    
    def generate_unique_id(self):
        """Generate and save a unique ID for the user"""
        while True:
            new_id = generate_unique_id()
            if not UserProfile.objects.filter(unique_id=new_id).exists():
                self.unique_id = new_id
                self.save(update_fields=['unique_id'])
                self.send_unique_id_email()
                return new_id
    
    def send_unique_id_email(self):
        """Send email with the unique ID"""
        if not self.unique_id:
            return
            
        subject = 'Your BoliBazaar Unique ID'
        html_message = render_to_string('emails/unique_id_email.html', {
            'user': self.user,
            'unique_id': self.unique_id,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            html_message=html_message,
            fail_silently=False,
        )

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