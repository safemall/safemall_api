from django.urls import path
from . import views


urlpatterns = [
    # API endpoint for registering buyers
    path('buyersignup/', views.BuyerSignupApi.as_view(), name='signup_api'),


    # API endpoint for logging buyers and vendors in
    path('login/', views.LoginApi.as_view(), name='login_api'),


    # API endpoint for registering vendors
    path('vendorsignup/', views.VendorSignupApi.as_view(), name='vendor_signup'),


    # API endpoint for opening vendor store after registration
    path('vendorstore/', views.VendorStoreApi.as_view(), name='vendor_store'),


    # API endpoint for uploading products from vendor store
    path('uploadproduct/', views.ProductUploadView.as_view(), name='upload_product'),


    # API endpoint for viewing product details and posting quantity of product to order
    path('productdetails/<int:product_id>/', views.ProductDetailsView.as_view(), name='product_details'),


    # API endpoint for making an order and getting an order confirmation code
    path('orderproduct/<int:product_id>/', views.OrderProductView.as_view(), name='order_product'),


    # API endpoint for viewing clothes category
    path('clothescategory/', views.ClothesPageView.as_view(), name='clothes_category'),


    # API endpoint for viewing food category
    path('foodcategory/', views.FoodPageView.as_view(), name='food_category'),


    # API endpoint for viewing footwear category
    path('footwearscategory/', views.FootwearsPageView.as_view(), name='footwear_category'),


    # API endpoint for viewing accessories category
    path('accessoriescategory/', views.AccessoriesPageView.as_view(), name='accessories_category'),


    # API endpoint for viewing beauty category
    path('beautycategory/', views.BeautyPageView.as_view(), name='beauty_category'),


    # API endpoint for viewing household category
    path('householdcategory/', views.HouseholdPageView.as_view(), name='household_category'),


    # API endpoint for viewing new arrivals
    path('newarrivals/', views.NewArrivalsView.as_view(), name='new_arrivals'),


    # API endpoint for viewing explore field
    path('explore/', views.ExploreView.as_view(), name='explore'),


    # API endpoint for viewing featured products
    path('featuredproduct/', views.FeaturedProductView.as_view(), name='featured_product'),


    #API endpoint for viewing vendor's page
    path('vendorpage/<uuid:vendor_id>/', views.VendorPageView.as_view(), name='vendor_page'),


    #API endpoint for viewing profile details
    path('profiledetails/', views.ProfileDetails.as_view(), name='profile_details'),


    #API endpoint for viewing buyer profile details
    path('vendorstoredetails/', views.VendorStoreDetails.as_view(), name='vendor_store_details'),

    
    #API endpoint for searching products based on product_name or vendor_name
    path('search/', views.SearchProduct.as_view(), name='search_product')
]