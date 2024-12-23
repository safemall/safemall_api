from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from django.utils import timezone
from django.conf import settings
import uuid
import secrets
# Create your models here.

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email_address"), unique=True)
    phone_number = models.CharField(max_length=20, default='')
    first_name = models.CharField(max_length=200, default='')
    last_name = models.CharField(max_length=200, default='')
    firebase_token = models.TextField(max_length=1000, default='')
    fcm_token = models.TextField(max_length=200, default='')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, related_name='user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='user_set', blank=True)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    

  
    

class BuyerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=10, default='')
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name
    
    class Meta:
        verbose_name = 'buyerprofile'
        verbose_name_plural = 'buyerprofiles'



class VendorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=10, default='')
    phone_number = models.CharField(max_length=15)
    vendor_id = models.UUIDField(default=uuid.uuid4())
    business_name = models.CharField(max_length=500)
    business_description = models.TextField(max_length=1000, default='')
    profile_image = models.ImageField(upload_to='image')
    business_address = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name
    
    class Meta:
        verbose_name = 'vendorprofile'
        verbose_name_plural = 'vendorprofiles'



class Product(models.Model):
    CATEGORIES = (
        ('clothes', 'clothes'),
        ('footwears', 'footwears'),
        ('accessories', 'accessories'),
        ('beauty', 'beauty'),
        ('household', 'household'),
        ('food', 'food')
    )
    product_name = models.CharField(max_length=200, null=True, blank=True)
    product_description = models.TextField(max_length=1000, null=True, blank=True)
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    vendor_identity = models.UUIDField(default='')
    vendor_name = models.CharField(max_length=500, null=True, blank=True)
    product_price = models.FloatField()
    discounted_amount = models.FloatField(default=0)
    discounted_price = models.FloatField(default=0)
    percentage_discount = models.IntegerField(default=0)
    product_category = models.CharField(choices=CATEGORIES, default='', max_length=50)
    stock = models.IntegerField(default=0)
    quantity_sold = models.IntegerField(default=0)
    product_image = models.ImageField(upload_to='image', null=True, blank=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='image', default='', null=True, blank=True)


class OrderDetail(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_id = models.UUIDField(default='')
    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    address = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=20)
    email_address = models.EmailField(max_length=500)
    product_name = models.CharField(max_length=200, null=True, blank=True)
    product_price = models.FloatField()
    vendor_name = models.CharField(max_length=500, null=True, blank=True)
    vendor_id = models.CharField(max_length=90,null=True, blank=True )
    product_quantity = models.IntegerField()
    total_price = models.FloatField()
    product_image = models.ImageField(upload_to='image', null=True)
    order_otp_token = models.CharField(max_length=8,default='')
    delivered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name
