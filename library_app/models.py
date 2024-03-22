from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=30, null=True)
    email = models.EmailField(unique=True, null=True) 
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    contact_number = models.CharField(max_length=15, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_approved = models.BooleanField(default=False, null=True)
    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, null=True)
    def __str__(self):
        return self.name
    


class Book(models.Model):
    name = models.CharField(max_length=200, null=True)
    author = models.CharField(max_length=100, null=True)
    publisher = models.CharField(max_length=100, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    stock = models.PositiveIntegerField(default=0)
    categories = models.ManyToManyField(Category)
    image = models.ImageField(upload_to='book_images/', blank=True, null=True)  
    def __str__(self):
        return self.name


class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rental_date = models.DateTimeField( null=True)
    return_date = models.DateTimeField(null=True) 
    returned_date = models.DateTimeField(null=True) 
    is_lost = models.BooleanField(default=False)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    request_date = models.DateTimeField(auto_now_add=True,null=True)
    is_rental_request = models.BooleanField(default=False,null=True)
    is_return_request = models.BooleanField(default=False,null=True)
    is_rental_approved = models.BooleanField(default=False,null=True)
    is_return_approved = models.BooleanField(default=False,null=True)

    
    def __str__(self):
        return f"{self.user.username} rented {self.book.name}"
    

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book, through='PurchaseItem',null=True)
    purchase_date = models.DateTimeField(auto_now_add=True,null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    
    # Billing Address
    billing_full_name = models.CharField(max_length=255, null=True, blank=True)
    billing_email = models.EmailField(null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True)
    billing_city = models.CharField(max_length=100, null=True, blank=True)
    billing_state = models.CharField(max_length=100, null=True, blank=True)
    billing_zip = models.CharField(max_length=20, null=True, blank=True)
    
    # Shipping Address
    shipping_full_name = models.CharField(max_length=255, null=True, blank=True)
    shipping_email = models.EmailField(null=True, blank=True)
    shipping_address = models.TextField(null=True, blank=True)
    shipping_city = models.CharField(max_length=100, null=True, blank=True)
    shipping_state = models.CharField(max_length=100, null=True, blank=True)
    shipping_zip = models.CharField(max_length=20, null=True, blank=True)
    
    # Payment Details
    card_name = models.CharField(max_length=255, null=True, blank=True)
    card_number = models.CharField(max_length=16, null=True, blank=True)
    expiration_month = models.CharField(max_length=2, null=True, blank=True)
    expiration_year = models.CharField(max_length=4, null=True, blank=True)
    cvv = models.CharField(max_length=4, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} purchased {', '.join([item.book.name for item in self.purchaseitem_set.all()])}"

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE,null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE,null=True)
    quantity = models.PositiveIntegerField(null=True)

    def __str__(self):
        return f"{self.purchase.user.username} purchased {self.quantity} copies of {self.book.name}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Book, through='CartItem')

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, null=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.username}: {self.message}"
