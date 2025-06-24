#!/usr/bin/env python3
"""
BoliBazaar Setup Script
Run this script to set up the auction website with sample data
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolibazaar.settings')
django.setup()

from django.contrib.auth.models import User
from auction.models import Product, Bid
from django.utils import timezone

def create_superuser():
    """Create admin user"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@bolibazaar.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print("Admin user created (username: admin, password: admin123)")
    else:
        print("Admin user already exists")

def create_demo_user():
    """Create demo user"""
    if not User.objects.filter(username='demo').exists():
        User.objects.create_user(
            username='demo',
            email='demo@bolibazaar.com',
            password='demo123',
            first_name='Demo',
            last_name='User'
        )
        print("Demo user created (username: demo, password: demo123)")
    else:
        print("Demo user already exists")

def create_sample_products():
    """Create sample auction products"""
    sample_products = [
        {
            'title': 'Vintage Camera',
            'description': 'A beautiful vintage camera from the 1960s. Perfect for collectors and photography enthusiasts.',
            'base_price': 5000.00,
            'end_time': timezone.now() + timedelta(days=3)
        },
        {
            'title': 'Antique Vase',
            'description': 'Elegant antique vase with intricate designs. A perfect centerpiece for your home.',
            'base_price': 2500.00,
            'end_time': timezone.now() + timedelta(days=2)
        },
        {
            'title': 'Classic Watch',
            'description': 'Luxury classic watch in excellent condition. A timeless piece for any collection.',
            'base_price': 15000.00,
            'end_time': timezone.now() + timedelta(days=5)
        },
        {
            'title': 'Rare Book Collection',
            'description': 'Collection of rare books including first editions. Perfect for book lovers and collectors.',
            'base_price': 8000.00,
            'end_time': timezone.now() + timedelta(days=4)
        },
        {
            'title': 'Artwork Painting',
            'description': 'Original oil painting by a renowned artist. A masterpiece for art enthusiasts.',
            'base_price': 25000.00,
            'end_time': timezone.now() + timedelta(days=6)
        }
    ]
    
    for product_data in sample_products:
        if not Product.objects.filter(title=product_data['title']).exists():
            Product.objects.create(**product_data)
            print(f"Created product: {product_data['title']}")
        else:
            print(f"Product already exists: {product_data['title']}")

def create_sample_bids():
    """Create sample bids"""
    demo_user = User.objects.get(username='demo')
    products = Product.objects.all()
    
    for product in products[:3]:  # Add bids to first 3 products
        if not Bid.objects.filter(product=product, bidder=demo_user).exists():
            bid_amount = product.base_price + 500
            Bid.objects.create(
                product=product,
                bidder=demo_user,
                amount=bid_amount
            )
            print(f"Created sample bid for {product.title}")

def main():
    print("Setting up BoliBazaar Auction Website...")
    print("=" * 50)
    
    try:
        create_superuser()
        create_demo_user()
        create_sample_products()
        create_sample_bids()
        
        print("=" * 50)
        print("Setup completed successfully!")
        print("\nLogin Credentials:")
        print("   Admin: username=admin, password=admin123")
        print("   Demo User: username=demo, password=demo123")
        print("\nTo start the server, run:")
        print("   python manage.py runserver")
        print("\nThen visit: http://127.0.0.1:8000")
        
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()