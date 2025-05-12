from django.urls import path
from . import views


urlpatterns = [
    # API endpoint for registering buyers
    path('buyersignup/', views.BuyerSignupApi.as_view(), name='signup_api'),


    path('ping/', views.ping),


    # API endpoint for logging buyers and vendors in
    path('login/', views.LoginApi.as_view(), name='login_api'),


    # API endpoint for registering vendors
    path('vendorsignup/', views.VendorSignupApi.as_view(), name='vendor_signup'),


    # API endpoint for opening, getting and updating vendor store after registration
    path('vendorstore/', views.VendorStoreApi.as_view(), name='vendor_store'),


    # API endpoint for uploading products from vendor store
    path('uploadproduct/', views.ProductUploadView.as_view(), name='upload_product'),


    # API endpoint for initiating chat
    path('initiatechat/', views.UserChatView.as_view(), name='initiate_chat'),


    # API endpoint for getting chatlists
    path('chatlist/', views.UserChatListView.as_view(), name='chatlist'),


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

    #API endpoint for subscriping vendors
    path('subscribevendor/', views.SubscriptionView.as_view(), name='vendor_subscription'),

    #API endpoint for setting transaction pin
    path('transactionpin/', views.SetTransactionPin.as_view(), name='transaction_pin'),

    #API endpoint for searching products based on product_name or vendor_name
    path('search/', views.SearchProduct.as_view(), name='search_product'),


    #API endpoint for getting product reviews
    path('getproductreview/<int:product_id>/', views.ProductReviewView.as_view(), name='product_review'),


    #API endpoint for posting product reviews
    path('postproductreview/<int:product_id>/<uuid:order_id>/', views.PostProductReviewView.as_view(), name='post_product_review'),


   #API endpoint for updating product reviews
    path('updateproductreview/<int:order_pk>/<int:product_id>/', views.UpdateProductReviewView.as_view(), name='update_product_review'),


    #API endpoint for posting product reviews
    path('userproductreview/', views.UserReviewsView.as_view(), name='user_product_review'),


    #API endpoint for getting orders made to a vendor
    path('vendororders/', views.VendorOrderView.as_view(), name='vendor_order'),


    #API endpoint for getting orders made by a buyer
    path('buyerorders/', views.BuyerOrderView.as_view(), name='buyer_orders'),


    #API endpoint for viewing products inventories
    path('inventories/', views.InventoryView.as_view(), name='inventories'),


    #API endpoint for sending email with otp to logged in user to reset password
    path('passwordreset/', views.PasswordResetView.as_view(), name='password_recovery'),


    #API endpoint for users to type in their email and receives an otp code if the email exists in database
    path('forgottenpassword/', views.ForgottenPasswordView.as_view(), name="forgotten_password"),


    #API endpoint for users to request for another otp in forgotten password
    path('resendotp/<str:email>/', views.ResendOtpView.as_view(), name='resend_otp'),


    #API endpoint for users to request for another otp in reset password
    path('resendotp/', views.ResendOtpCodeView.as_view(), name='resend_otp'),


    #API endpoint for users to verify the otp token sent to their email in forgotten password
    path('otpverification/<str:email>/', views.OtpVerificationView.as_view(), name='otp_verification'),


    #API endpoint for users to verify the otp token sent to their emaill in reset password
    path('otpverification/', views.OtpCodeVerificationView.as_view(), name='otpcode_verification'),


    #API endpoint for sending email with otp to logged in user to reset transaction pin
    path('resettransactionpin/', views.ResetTransactionPinView.as_view(), name='reset_transaction_pin'),


    #API endpoint for verifying the otp token sent to user's email in reset transaction pin
    path('verifytransactionotp/', views.VerifyTransactionOtp.as_view(), name='verify_transaction_otp'),


    #API endpoint for checking if the inputted password is correct
    path('checkpassword/', views.CheckPasswordView.as_view(), name="check_password"),


    #API endpoint for changing the user's email with the inputted one
    path('resetemail/', views.ResetEmailView.as_view(), name='reset_email'),


    #API endpoint for sending email verification code to users
    path('verifyemail/', views.EmailVerificationView.as_view(), name='email_verification'),

    
    #API endpoint for verifying the otp code sent to user's email for email verification 
    path('verifyotp/', views.EmailOtpVerificationView.as_view(), name='verify_otp'),


    path('deposit/', views.DepositMoneyView.as_view(), name='deposit_money'),

    path('verifydeposit/', views.VerifyDepositView.as_view(), name='verify_deposit'),

    path('withdrawal/', views.WithdrawFundsView.as_view(), name='withdrawal'),

    path('findrecipient/', views.FindRecipientView.as_view(), name='find_recipient')
]
