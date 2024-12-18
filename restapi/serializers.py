from rest_framework import serializers
from django.conf import settings
from .models import BuyerProfile, VendorProfile, Product, OrderDetail
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False)

    class Meta:
        user = get_user_model()
        model = user
        fields = ['id','phone_number', 'firebase_token', 'fcm_token', 'email', 'first_name', 'last_name', 'password']
        
    def to_internal_value(self, data):
        User = get_user_model()
        if 'email' not in data and 'password' not in data:
            return data
        email = data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({'error': 'email already exists'})
            return super().to_internal_value(data)
        

class BuyerSerializer(serializers.ModelSerializer):

    class Meta:
        model = BuyerProfile
        fields = ['phone_number', 'email', 'first_name', 'account_number', 'last_name']


class VendorSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False, allow_null=True)
    business_address = serializers.CharField(required=False)
    business_description = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    business_name = serializers.CharField(required=False)

    class Meta:
        model = VendorProfile
        fields = ['business_name', 'phone_number', 'business_description', 'business_address', 'account_number', 'profile_image']
        read_only_fields = ['account_number']

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_description', 'vendor_identity', 'vendor_name',  'product_price', 'product_category', 'stock', 'quantity_sold', 'product_image1', 'product_image2', 'product_image3', 'product_image4']
        
        vendor_name = serializers.CharField(required=False)
        product_image1 = serializers.ImageField(allow_null=True)
        product_image2 = serializers.ImageField(allow_null=True)
        product_image3 = serializers.ImageField(allow_null=True)
        product_image4 = serializers.ImageField(allow_null=True)
        extra_kwargs = {
            'quantity_sold': {'required': False},
        }


class OrderDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model  = OrderDetail
        fields = ['order_id', 'first_name', 'last_name', 'address', 'email_address', 'phone_number', 'product_name', 'product_price', 'vendor_name', 'product_quantity', 'total_price', 'product_image', 'order_otp_token', 'delivered', 'created_at']

        vendor_name = serializers.CharField(required=False)
        product_image = serializers.ImageField(allow_null=True)
        product_name = serializers.CharField(required=False)
        extra_kwargs = {
            'product_price': {'required': False},
            'product_quantity': {'required': False},
            'total_price': {'required': False}
        }