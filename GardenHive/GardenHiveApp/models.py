from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now 
from datetime import timedelta
# Custom User Modele

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email =  models.EmailField(max_length=150, unique=True, null=True, blank=True)
    is_admin = models.BooleanField(default=True)  

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
   

class Login(models.Model):
    username = models.CharField(max_length=150, unique=True, default="default_user")
    password = models.CharField(max_length=150, default="defaultpassword")
    email = models.EmailField(max_length=150, unique=True, null=True, blank=True)
    types = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('user', 'User'), ('nursery', 'Nursery')], default='user')
    status = models.CharField(max_length=10, default='1')  

    def __str__(self):
        return self.username

class Nursery(models.Model):
    logid = models.ForeignKey(Login, on_delete=models.CASCADE, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nursery', null=True, blank=True)
    name = models.CharField(max_length=150, null=True)
    addr = models.CharField(max_length=150, null=True)
    location = models.CharField(max_length=100,choices=[("Thiruvananthapuram", "Thiruvananthapuram"), ("Kollam", "Kollam"), ("Alappuzha", "Alappuzha"), ("Pathanamthitta", "Pathanamthitta"), ("Kottayam", "Kottayam"), ("Idukki", "Idukki"), ("Ernakulam", "Ernakulam"), ("Thrissur", "Thrissur"), ("Palakkad", "Palakkad"), ("Malappuram", "Malappuram"), ("Kozhikode", "Kozhikode"), ("Wayanad", "Wayanad"), ("Kannur", "Kannur"), ("Kasaragod", "Kasaragod")], default='Not specified')
    owner = models.CharField(max_length=150, null=True)
    lcnno = models.CharField(max_length=100, null=True) 
    email = models.EmailField(max_length=150, null=True)
    phno = models.CharField(max_length=10, null=True)
    username = models.CharField(max_length=150, null=True)
    status = models.CharField(max_length=10, choices=[("0", "Pending"), ("1", "Approved"), ("-1", "Rejected")], default='0', null=True)  

    def __str__(self):
        return self.name

class Staff(models.Model):
    nursery = models.ForeignKey(Nursery, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=50, choices=[('Manager', 'Manager'), ('Sales', 'Sales'), ('Support', 'Support')], default='Staff')
    date_joined = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='staff_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.role} at {self.nursery.name}"

class UserProfile(models.Model):
    logid = models.OneToOneField(Login, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=150, null=True)
    address = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
    location = models.CharField(max_length=100,choices=[("Thiruvananthapuram", "Thiruvananthapuram"), ("Kollam", "Kollam"), ("Alappuzha", "Alappuzha"), ("Pathanamthitta", "Pathanamthitta"), ("Kottayam", "Kottayam"), ("Idukki", "Idukki"), ("Ernakulam", "Ernakulam"), ("Thrissur", "Thrissur"), ("Palakkad", "Palakkad"), ("Malappuram", "Malappuram"), ("Kozhikode", "Kozhikode"), ("Wayanad", "Wayanad"), ("Kannur", "Kannur"), ("Kasaragod", "Kasaragod")])
    phone = models.CharField(max_length=15)
    email=models.EmailField(max_length=150, null=True)
    status = models.CharField(max_length=10, default='1')  

    def __str__(self):
        return self.user.username
    
class CareTip(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=now)  

    def __str__(self):
        return f"{self.title} ({self.category.name})"

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, null=True, blank=True, default=1)
    size = models.CharField(max_length=50, blank=True)
    nursery = models.ForeignKey("Nursery", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        subcategory_name = self.subcategory.name if self.subcategory else "No Subcategory"
        return f"{self.name} - {self.category.name} - {subcategory_name}"

class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)  # Allow NULL for guests
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} - {self.product.name} ({self.quantity})"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booked_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')], default='pending')
    cancel_deadline = models.DateTimeField(default=timezone.now() + timedelta(days=10))

    def save(self, *args, **kwargs):
        if not self.cancel_deadline:
            self.cancel_deadline = self.booking_date + timedelta(days=10)
        super().save(*args, **kwargs)

    def can_cancel(self):
        return timezone.now() <= self.cancel_deadline

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.booking_date.strftime('%Y-%m-%d')}"

