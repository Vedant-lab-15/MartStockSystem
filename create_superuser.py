import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_mart.settings')
django.setup()

from django.contrib.auth.models import User

# Check if superuser already exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
    print("Superuser 'admin' created with password 'adminpass'")
else:
    print("Superuser 'admin' already exists")