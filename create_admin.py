import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolibazaar.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import IntegrityError

# Create or update admin user
try:
    # Try to get existing admin user
    admin = User.objects.get(username='admin6397664902')
    admin.set_password('Aryan@010')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print("Admin user updated successfully!")
except User.DoesNotExist:
    # Create new admin user
    User.objects.create_superuser(
        username='admin6397664902',
        email='admin@bolibazaar.com',
        password='Aryan@010',
        first_name='Admin',
        last_name='User'
    )
    print("Admin user created successfully!")
except IntegrityError:
    print("Error: Username already exists but couldn't be updated.")