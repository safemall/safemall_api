from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Product, ProductReview, VendorProfile
from django.core.cache import cache



@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):

    cache.delete_pattern('*product_details*')
    cache.delete_pattern('*new_arrivals*')
    cache.delete_pattern('*product_category*')
    cache.delete_pattern('*product_reviews*')
    cache.delete_pattern('*vendor_page*')
    cache.delete_pattern('*featured_products*')



@receiver([post_save, post_delete], sender=ProductReview)
def invalidate_product_review_cache(sender, instance, **kwargs):

    cache.delete_pattern('*product_reviews*')


@receiver([post_save, post_delete], sender=VendorProfile)
def invalidate_vendor_store_cache(sender, instance, **kwargs):

    cache.delete_pattern('*vendor_page*')
    cache.delete_pattern('*explore*')