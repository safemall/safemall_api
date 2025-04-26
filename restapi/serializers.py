from rest_framework import serializers
from django.conf import settings
from .models import BuyerProfile, VendorProfile, Product, OrderDetail, ProductImage, ProductReview, Wallet, TransactionHistory
from django.contrib.auth import get_user_model
from django.utils import timesince


class UnwrappedListField(serializers.Field):
    def to_representation(self, data):
        if isinstance(data, list):
            return data[0]
        return data

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False)
    profile_image = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True, use_url=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    fcm_token = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    firebase_token = serializers.CharField(required=False)
    transaction_pin = serializers.CharField(required=False)
    email_verified = serializers.BooleanField(required=False)
    firebase_user_id = serializers.CharField(required=False)

    class Meta:
        user = get_user_model()
        model = user
        fields = ['id','phone_number', 'firebase_token', 'firebase_user_id', 'profile_image', 'fcm_token', 'email', 'email_verified', 'school', 'transaction_pin', 'first_name', 'last_name', 'password']
    
    def to_internal_value(self, data):
        User = get_user_model()
        if 'email' not in data and 'password' not in data:
            return data
        email = data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({'error': 'email already exists'})
            return super().to_internal_value(data)
        
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if isinstance(value, list) and len(value) == 1:
                validated_data[key] = value[0]
        return super().update(instance, validated_data)     
    
        

class BuyerSerializer(serializers.ModelSerializer):

    class Meta:
        model = BuyerProfile
        fields = ['phone_number', 'email', 'first_name', 'account_number', 'last_name']


class VendorSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False, allow_null=True, use_url=True)
    business_address = serializers.CharField(required=False)
    business_description = serializers.CharField(required=False)
    business_phone_number = serializers.CharField(required=False)
    business_name = serializers.CharField(required=False)
    vendor_email = serializers.EmailField(required=False)
    vendor_id = serializers.UUIDField(required=False)
    firebase_user_id = serializers.CharField(required=False)

    class Meta:
        model = VendorProfile
        fields = ['business_name', 'business_phone_number', 'vendor_id', 'firebase_user_id',  'vendor_email', 'business_description', 'business_address', 'account_number', 'profile_image']
        read_only_fields = ['account_number']


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    updated_at = serializers.DateTimeField(required=False)

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'average_rating', 'school', 'product_description', 'discounted_price', 'percentage_discount', 'discounted_amount', 'vendor_identity', 'vendor_name', 'vendor_image',  'product_price', 'product_category', 'stock', 'quantity_sold', 'uploaded_at', 'updated_at',
                  'images']
        
        vendor_name = serializers.CharField(required=False)
       
        extra_kwargs = {
            'quantity_sold': {'required': False},
            'discounted_amount': {'required': False},
            'discounted_price':  {'required': False},
            'percentage_discount': {'required': False},
        }

        def to_internal_value(self, data):
            product = Product
            if 'discounted_amount' not in data and 'product_price' not in data:
                return data
            discount = data.get('discounted_amount')
            price = data.get('product_price')
            if discount | price:
                if discount > price:
                    raise serializers.ValidationError({'error': 'Product discount cannot be greater than product price'})
                return super().to_internal_value(data)
            
        


class OrderDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model  = OrderDetail
        fields = ['id', 'order_id', 'first_name', 'last_name', 'address', 'email_address', 'phone_number', 'product_name', 'product_price', 'product_image', 'vendor_name', 'product_quantity', 'total_price', 'order_otp_token', 'order_status', 'created_at']

        vendor_name = serializers.CharField(required=False)   
        product_name = serializers.CharField(required=False)
        product_image = serializers.ImageField(required=False, allow_null=True)
        extra_kwargs = {
            'product_price': {'required': False},
            'product_quantity': {'required': False},
            'total_price': {'required': False}
        }


class OrderDetailForVendorsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrderDetail
        fields = ['order_id', 'first_name', 'last_name', 'address', 'email_address', 'phone_number', 'product_name', 'product_price', 'product_image', 'vendor_name', 'product_quantity', 'total_price', 'order_status', 'payment_status', 'created_at']
        


class ProductReviewSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'product', 'first_name', 'last_name', 'rating', 'review', 'image', 'created_at', 'edited_at']
        read_only_fields = ['user', 'created_at', 'product', 'first_name', 'last_name', 'image', 'edited_at']


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = ['account_number', 'first_name', 'last_name', 'funds']



class TransferWalletSerializer(WalletSerializer):

    class Meta:
        model = Wallet
        exclude = ['funds', 'id', 'user']



class TransactionSerializer(serializers.ModelSerializer):

    transaction = serializers.CharField(required=False)
    transaction_type = serializers.CharField(required=False)
    transaction_id = serializers.CharField(required=False)
    recipient = serializers.CharField(required=False)
    sender = serializers.CharField(required=False)
    product_name = serializers.CharField(required=False)
    product_quantity = serializers.CharField(required=False)

    class Meta:
        model = TransactionHistory
        fields = ['transaction', 'transaction_type', 'transaction_id', 'transaction_amount', 'recipient', 'sender', 'product_name', 'product_quantity', 'created_at']
