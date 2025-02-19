from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, BuyerProfile, TransactionPercentage, VendorProfile, OrderDetail, Product, ProductImage, ProductReview,Wallet, Pending, TransactionHistory

# Register your models here.


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("email", "is_staff", "is_active", )
    list_filter = ("email", "is_staff", "is_active", )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("permissions", {"fields": ("is_staff", "is_active","groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff", "is_active", "groups", "user_permissions"
            )
        }),
    )

    search_fields = ("email", )
    ordering = ("email",)


class BuyerDisplay(admin.ModelAdmin):
    list_display = ['first_name', 'email', 'account_number', 'created_at']
    readonly_fields = ['first_name', 'email', 'account_number', 'last_name', 'phone_number', 'user']


class VendorDisplay(admin.ModelAdmin):
    list_display = ['business_name', 'vendor_id', 'account_number', 'created_at']
    readonly_fields = ['business_name', 'profile_image', 'account_number', 'vendor_id', 'business_address', 'business_description', 'business_phone_number', 'user']


class ProductDisplay(admin.ModelAdmin):
    list_display = ['product_name', 'vendor_name', 'product_price', 'uploaded_at']
    readonly_fields = ['product_name', 'product_description', 'vendor', 'vendor_identity', 'vendor_name', 'product_price', 'discounted_amount', 'discounted_price',
                       'percentage_discount', 'product_category', 'stock', 'quantity_sold', 'vendor_image']


class OrderDisplay(admin.ModelAdmin):
    list_display = ['first_name', 'order_id', 'product_name', 'created_at']
    readonly_fields = ['user', 'order_id', 'first_name', 'last_name', 'address', 'phone_number', 'email_address', 'product_name', 'product_price', 'vendor_name', 'vendor_id',
                       'product_quantity', 'product_image', 'total_price', 'order_otp_token']


class ProductReviewDisplay(admin.ModelAdmin):
    list_display = ['first_name', 'rating', 'review', 'created_at']
    readonly_fields = ['first_name', 'last_name', 'product', 'user', 'vendor_id', 'rating', 'review', 'image']


class WalletDisplay(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'account_number', 'funds']
    readonly_fields = ['user','first_name', 'last_name', 'account_number']


class PendingDisplay(admin.ModelAdmin):
    list_display = ['order_id', 'otp_token', 'amount', 'created_at']



class TransactionHistoryDisplay(admin.ModelAdmin):
    list_display = ['transaction', 'transaction_type', 'transaction_amount', 'created_at']


class TransactionPercentageDisplay(admin.ModelAdmin):
    list_display = ['name', 'balance']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(BuyerProfile, BuyerDisplay)
admin.site.register(VendorProfile, VendorDisplay)
admin.site.register(OrderDetail, OrderDisplay)
admin.site.register(Product, ProductDisplay)
admin.site.register(ProductImage)
admin.site.register(Wallet, WalletDisplay)
admin.site.register(Pending, PendingDisplay)
admin.site.register(ProductReview, ProductReviewDisplay)
admin.site.register(TransactionHistory,  TransactionHistoryDisplay)
admin.site.register(TransactionPercentage, TransactionPercentageDisplay)
