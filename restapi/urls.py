from django.urls import path
from . import views


urlpatterns = [
    # API endpoint for registering buyers
    path('buyersignup/', views.BuyerSignupApi.as_view(), name='signup_api'),


    # API endpoint for logging buyers and vendors in
    path('login/', views.LoginApi.as_view(), name='login_api'),


    # API endpoint for registering vendors
    path('vendorsignup/', views.VendorSignupApi.as_view(), name='vendor_signup'),


    # API endpoint for opening, getting and updating vendor store after registration
    path('vendorstore/', views.VendorStoreApi.as_view(), name='vendor_store'),


    # API endpoint for uploading products from vendor store
    path('uploadproduct/', views.ProductUploadView.as_view(), name='upload_product'),


    # API endpoint for paying vendors after order otp verification
    path('vendorpayment/', views.VendorPayment.as_view(), name='vendor_payment'),


    path('transfer/', views.TranferView.as_view(), name='transfer'),


    #API endpoint for viewing transaction history
    path('transactionhistory/', views.TransactionHistoryView.as_view(), name='transaction_history'),


    # API endpoint for viewing wallet
    path('wallet/', views.WalletView.as_view(), name='wallet'),


    # API endpoint for viewing product details and posting quantity of product to order
    path('productdetails/<int:product_id>/', views.ProductDetailsView.as_view(), name='product_details'),


    path('productdetails/<int:product_id>/images/<int:image_id>/', views.ProductImageView.as_view(), name='delete_product_image'),


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


    path('subscripevendor/', views.SubscriptionView.as_view(), name='vendor_subscription'),

    
    path('transactionpin/', views.SetTransactionPin.as_view(), name='transaction_pin'),

    #API endpoint for searching products based on product_name or vendor_name
    path('search/', views.SearchProduct.as_view(), name='search_product'),


    #API endpoint for getting and posting product reviews
    path('productreview/<int:product_id>/', views.ProductReviewView.as_view(), name='product_review'),


    #API endpoint for getting orders made to a vendor
    path('vendororders/', views.VendorOrderView.as_view(), name='vendor_order'),


    #API endpoint for getting orders made by a buyer
    path('buyerorders/', views.BuyerOrderView.as_view(), name='buyer_orders'),


    #API endpoint for viewing products inventories
    path('inventories/', views.InventoryView.as_view(), name='inventories')
]