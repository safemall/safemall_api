from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission 
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from django.utils import timezone
from django.conf import settings
from .schools import SCHOOLS
from django.utils import timezone
import uuid
import secrets
from decimal import Decimal
# Create your models here.

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email_address"), unique=True)
    phone_number = models.CharField(max_length=20, default='')
    first_name = models.CharField(max_length=200, )
    last_name = models.CharField(max_length=200, )
    school = models.CharField(max_length=1000, choices=SCHOOLS, default='')
    firebase_token = models.TextField(max_length=1000, )
    email_verified = models.BooleanField(default=False)
    transaction_pin = models.CharField(max_length=255, default='')
    fcm_token = models.TextField(max_length=200, default='')
    profile_image = models.ImageField(upload_to='image', null=True, default='', blank=True)
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
    


class OtpTokenGenerator(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp_token = models.CharField(max_length=6)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)



class TransactionOtpTokenGenerator(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp_token = models.CharField(max_length=6)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)
  

class EmailOtpTokenGenerator(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp_token = models.CharField(max_length=6)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)

class BuyerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=10, default='')
    phone_number = models.CharField(max_length=15)
    buyer_id = models.CharField(default='', max_length=90)
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
    business_phone_number = models.CharField(max_length=15, default='', null=True, blank=True)
    vendor_id = models.UUIDField(default=uuid.uuid4())
    vendor_email = models.EmailField(max_length=200, default='')
    business_name = models.CharField(max_length=500, default='')
    business_description = models.TextField(max_length=1000, default='')
    profile_image = models.ImageField(upload_to='image')
    business_address = models.CharField(max_length=500)
    subscription_status = models.BooleanField(default=False)
    subscription_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name
    
    class Meta:
        verbose_name = 'vendorprofile'
        verbose_name_plural = 'vendorprofiles'


    def is_subscriped(self):
        if self.subscription_status == True and self.subscription_expires_at > timezone.now():
            return True
        else:
            return False
        

    def subscripe_for_two_hours(self):
        self.subscription_status = True
        self.subscription_expires_at = timezone.now() + timezone.timedelta(hours=2)
        self.save()

    
    def subscripe_for_two_minutes(self):
        self.subscription_status = True
        self.subscription_expires_at = timezone.now() + timezone.timedelta(minutes=2)
        self.save()


    def unsubscripe(self):
        self.subscription_status = False
        self.subscription_expires_at = None
        self.save()




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
    school = models.CharField(default='', max_length=1000, blank=True)
    percentage_discount = models.IntegerField(default=0)
    product_category = models.CharField(choices=CATEGORIES, default='', max_length=50)
    stock = models.IntegerField(default=0)
    quantity_sold = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0)
    vendor_image = models.ImageField(upload_to='image', null=True, blank=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='image', default='', null=True, blank=True)



class OrderDetail(models.Model):
    ORDER_STATUS = (
        ('Pending', 'Pending'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    )

    PAYMENT_STATUS = (
        ('Paid, Pending Confirmation', 'Paid, Pending Confirmation'),
        ('Paid and Confirmed', 'Paid and Confirmed'),
        ('Payment Reversed', 'Payment Reversed')
    )


    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_id = models.UUIDField(default='')
    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    address = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=20)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS, default='Pending')
    email_address = models.EmailField(max_length=500)
    product_name = models.CharField(max_length=200, null=True, blank=True)
    product_image = models.ImageField(upload_to='image', default='', null=True, blank=True)
    product_price = models.FloatField()
    vendor_name = models.CharField(max_length=500, null=True, blank=True)
    vendor_id = models.CharField(max_length=90,null=True, blank=True )
    product_quantity = models.IntegerField()
    total_price = models.FloatField()
    order_otp_token = models.CharField(max_length=8,default='')
    payment_status = models.CharField(max_length=60, choices=PAYMENT_STATUS, default='Paid, Pending Confirmation')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.first_name


class ProductReview(models.Model):
    RATING = (
        (1, '1-Poor'),
        (2, '2-Fair'),
        (3, '3-Good'),
        (4, '4-Very Good'),
        (5, '5-Excellent')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_review')
    vendor_id = models.CharField(max_length=200, default='')
    first_name = models.CharField(max_length=200, default='')
    last_name = models.CharField(max_length=200, default='')
    rating = models.IntegerField(choices=RATING, default=1)
    review = models.TextField(max_length=1000)
    image = models.ImageField(upload_to='image', null=True, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name
    

class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_wallet')
    account_number = models.CharField(max_length=10)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    funds = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)


    def deposit(self, amount):
        decimal_amount = Decimal(amount)
        self.funds += decimal_amount
        self.save()

    def withdraw(self, amount):
        decimal_amount = Decimal(amount)
        if self.funds > decimal_amount:
            self.funds -= decimal_amount
            self.save()
            return True
        return False
    

class Pending(models.Model):
    product_id = models.IntegerField(default=0)
    order_id = models.CharField(max_length=80)
    account_number = models.CharField(max_length=10, default='')
    otp_token = models.CharField(max_length=10)
    quantity = models.IntegerField(default=0)
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    reverse_payment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class TransactionHistory(models.Model):
    CHOICES = (
        ('Order', 'Order'),
        ('Reverse payment', 'Reverse payment'),
        ('Transfer', 'Transfer'),
        ('Deposit', 'Deposit'),
    )

    TRANSACTION = (
        ('Debit', 'Debit'),
        ('Credit', 'Credit')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction = models.CharField(max_length=20, choices=TRANSACTION, default='')
    transaction_type = models.CharField(max_length=20, choices=CHOICES, default='')
    transaction_amount = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    sender = models.CharField(max_length=500, default='')
    recipient = models.CharField(max_length=20, default='')
    product_name = models.CharField(max_length=200, default='')
    product_quantity = models.CharField(max_length=20, default='')
    created_at = models.DateTimeField(auto_now_add=True)



class TransactionPercentage(models.Model):
    name = models.CharField(max_length=50, default='Transaction percentage')
    balance = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    reset = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

class SubscriptionFunds(models.Model):
    name = models.CharField(max_length=50, default='Subscription funds')
    balance = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    reset = models.BooleanField(default=False)