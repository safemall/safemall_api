from django.shortcuts import render
from rest_framework.response import Response
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.http import Http404
from .serializers import UserSerializer, BuyerSerializer, VendorSerializer, ProductSerializer,OrderDetailForVendorsSerializer, OrderDetailSerializer, ProductImageSerializer, ProductReviewSerializer, WalletSerializer, TransactionSerializer, TransferWalletSerializer
from .models import BuyerProfile, VendorProfile, Product,TransactionPercentage , OrderDetail, ProductImage, ProductReview, Pending, Wallet, TransactionHistory
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models.fields.files import ImageFieldFile
from .transaction import Transaction, TransferFunds
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
import secrets
from django.views.decorators.vary import vary_on_headers
import random 
from decimal import Decimal
import uuid
from django.core.cache import cache
from django.db.models import Avg
from django.utils import timezone
import pyfcm
import paystack
# Create your views here.

#signup API for registering buyers
class BuyerSignupApi(APIView):
    
    
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        User = get_user_model()
        
        if User.objects.filter(email=request.data['email']).exists():
            return Response({'message': 'Email already exists'})
        else:
            if serializer.is_valid():        
                serializer.save()
                buyer = get_object_or_404(User, email= request.data['email'])
                buyer.set_password(request.data['password'])
                buyer.save()
                buyer_profile = BuyerProfile.objects.create(user=buyer, buyer_id=uuid.uuid4(), email=buyer.email, account_number='2' + str(uuid.uuid4().int)[:10-len('2')], first_name=buyer.first_name, last_name=buyer.last_name, phone_number=request.data['phone_number'])
                buyer_profile.save()
                wallet = Wallet.objects.create(user = buyer, account_number = buyer_profile.account_number, first_name=buyer.first_name, last_name = buyer.last_name)
                wallet.save()
                token = Token.objects.create(user=buyer)
                data = {
                    'token': token.key,
                    'buyer': serializer.data
                }
                return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


#signup API for registering vendors

class VendorSignupApi(APIView):

    
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        User = get_user_model()
        if User.objects.filter(email=request.data['email']).exists():
                return Response({'message': 'Email already exists'})
        else:
            if serializer.is_valid():
                serializer.save()
                vendor = get_object_or_404(User, email=request.data['email'])
                vendor.set_password(request.data['password'])
                vendor.save()
                token = Token.objects.create(user=vendor)
                token.save()
                vendor_profile = VendorProfile.objects.create(user=vendor, vendor_email=vendor.email, business_name='', profile_image='', account_number= '2' + str(uuid.uuid4().int)[:10-len('2')], business_address='', business_phone_number='')
                vendor_profile.save()
                wallet = Wallet.objects.create(user=vendor, account_number=vendor_profile.account_number, first_name=vendor.first_name, last_name=vendor.last_name)
                wallet.save()
                data = {
                    'token': token.key,
                    'vendor': serializer.data
                }
                return Response(data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

    
# login API for logging both vendors and buyers in

class LoginApi(APIView):

    
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        fcm_token = request.data['fcm_token']
        firebase_token = request.data['firebase_token']
        user = authenticate(email=email, password=password)
        User = get_user_model()

        if user is not None:
            
            if BuyerProfile.objects.filter(user=user).exists():
                buyer = get_object_or_404(BuyerProfile, user=user)
                serializer = BuyerSerializer(buyer)
                auth_user = User.objects.get(email=email)
                auth_user.fcm_token = fcm_token
                auth_user.firebase_token = firebase_token
                auth_user.save()
                user_serializer = UserSerializer(auth_user)
                token, created = Token.objects.get_or_create(user=user)
                data = {
                    'token': token.key,
                    'user': serializer.data,
                    'auth_user': user_serializer.data,
                    'user_type': 'buyer'
                }
                return Response(data)
            
            else:
                vendor = get_object_or_404(VendorProfile, user=user)
                vendor_serializer = VendorSerializer(vendor)
                auth_user = User.objects.get(email=email)
                auth_user.fcm_token = fcm_token
                auth_user.firebase_token = firebase_token
                auth_user.save()
                user_serializer = UserSerializer(auth_user)
                token, created = Token.objects.get_or_create(user=user)
                data = {
                    'token': token.key,
                    'user': vendor_serializer.data,
                    'auth_user': user_serializer.data,
                    'user_type': 'vendor'
                }
                return Response(data)
        return Response({'message': 'invalid credentials'}, status=status.HTTP_404_NOT_FOUND)



class VendorStoreApi(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request):
        user = get_object_or_404(VendorProfile, user=request.user)
        serializer = VendorSerializer(user)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = VendorSerializer(data=request.data)
        user = request.user
        vendor = get_object_or_404(VendorProfile, user=user)
        vendor.business_name = request.data['business_name']
        vendor.business_address = request.data['business_address']
        vendor.business_description = request.data['business_description']
        vendor.profile_image = request.FILES.get('profile_image', None)
        vendor.business_phone_number = request.data['business_phone_number']
        vendor.subscription_expires_at = timezone.now() + timezone.timedelta(days=5)
        vendor.subscription_status = True 
        vendor.save()
        Vendorstore = VendorSerializer(vendor)
        return Response(Vendorstore.data, status=status.HTTP_201_CREATED)
    
    def put(self, request):
        user = get_object_or_404(VendorProfile, user=request.user)
        serializer = VendorSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            if request.data['business_name']:
                products = Product.objects.filter(vendor_identity = user.vendor_id)
                for product in products:
                    product.vendor_name = request.data['business_name']
                    product.save()
            if request.data['profile_image']:
                products = Product.objects.filter(vendor_identity = user.vendor_id)
                for product in products:
                    product.vendor_image = request.data['profile_image']
                    product.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class SetTransactionPin(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pin = request.data['pin']
        user = request.user
        if 'pin' in request.data:
            if pin:
                user.transaction_pin = make_password(pin)
                user.save()
                return Response({'message': 'Pin set successfully'})
            else:
                return Response({'message': 'Please input a valid pin'})
        else:
            return Response({'message': 'Pin is required'})


class SubscriptionView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vendor = get_object_or_404(VendorProfile, user=request.user)
        vendor.subscripe_for_two_hours()
        return Response({'message': 'You are subscriped for 2 hours'})



class ProductUploadView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    
    def post(self, request):
        user = request.user
        vendor = get_object_or_404(VendorProfile, user=user)
        if vendor.subscription_expires_at is not None and vendor.subscription_expires_at < timezone.now():
            vendor.unsubscripe()
        if vendor.is_subscriped():
            name = vendor.business_name
            identity = vendor.vendor_id
            vendor_image = vendor.profile_image
            serializer = ProductSerializer(data=request.data)
            if vendor.business_name == '':
                return Response({"message": "You haven't set up your store"})
            else:
                if int(request.data['discounted_amount']) > int(request.data['product_price']):
                    return Response({'message': 'product discount cannot be greater than product price'})
                else:
                    if serializer.is_valid():
                        product = Product.objects.create(vendor=vendor, product_name=request.data['product_name'], vendor_image=vendor_image, discounted_amount=request.data['discounted_amount'], stock=request.data['stock'], product_description=request.data['product_description'], product_category=request.data['product_category'], vendor_name=name,
                                                        vendor_identity=identity, product_price=request.data['product_price'])
                        price = int(product.discounted_amount) / int(product.product_price)
                        discounted_price = int(product.product_price) - int(product.discounted_amount)
                        percentage = price * 100
                        product.percentage_discount = percentage
                        product.discounted_price = discounted_price
                        product.save()
                        images = request.FILES.getlist('uploaded_images')
                        for image in images:
                            new_product_image = ProductImage.objects.create(product=product, image=image)
                            
                        product_serializer = ProductSerializer(product)
                        return Response( product_serializer.data, status=status.HTTP_201_CREATED)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Subscription is out of date'})
        


class ProductDetailsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get_object(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise Http404

    #@method_decorator(cache_page(60 * 15, key_prefix='product_details'))
    def get(self, request, product_id):
        product = self.get_object(product_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
        

       
    def post(self, request, product_id):
        product = self.get_object(product_id)
        vendor = VendorProfile.objects.filter(user=request.user).first()
        if vendor:
            if product.vendor_identity == vendor.vendor_id:
                return Response({'message': 'You cannot order your own product'})
            else:
                quantity = int(request.data['quantity'])
                serializer = ProductSerializer(product)
                if int(quantity) < int(product.stock):
                    cache_key = f'user_{request.user.id}_order_for_{product_id}_cache_key'
                    cache.set(cache_key, quantity, 3600)
                    data = {
                        'product': serializer.data,
                        'quantity': quantity
                    }
                    return Response(data)
                else:
                    return Response({'message': 'product stock is not up to the quantity inputted'})

        else:
            quantity = int(request.data['quantity'])
            serializer = ProductSerializer(product)
            if int(quantity) < int(product.stock):
                cache_key = f'user_{request.user.id}_order_for_{product_id}_cache_key'
                cache.set(cache_key, quantity, 3600)
                data = {
                    'product': serializer.data,
                    'quantity': quantity
                }
                return Response(data)
            else:
                return Response({'message': 'product stock is not up to the quantity inputted'})            
        

        
    def patch(self, request, product_id):
        product = self.get_object(product_id)
        serializer = ProductSerializer(product, data=request.data)
        vendor = get_object_or_404(VendorProfile, user=request.user)
        if vendor.subscription_expires_at is not None and vendor.subscription_expires_at < timezone.now():
            vendor.unsubscripe()
        if vendor.is_subscriped():
            if vendor.vendor_id == product.vendor_identity:
                if int(request.data['discounted_amount']) > int(request.data['product_price']):
                    return Response({'message': 'product discount cannot be greater than product price'})
                else:
                    if serializer.is_valid():
                        serializer.save()
                        price = int(product.discounted_amount) / int(product.product_price)
                        discounted_price = int(product.product_price) - int(product.discounted_amount)
                        percentage = price * 100
                        product.percentage_discount = percentage
                        product.discounted_price = discounted_price
                        product.save()

                        image_id = request.data.get('image_id')
                        new_image = request.FILES.getlist('uploaded_images')
                        updated_image = request.FILES.get('updated_image')
                        if image_id and updated_image:
                            existing_image = product.images.get(id=image_id)
                            existing_image.image = updated_image
                            existing_image.save()
                        else:
                            for image in new_image:
                                ProductImage.objects.create(product=product, image=image)
                        return Response(serializer.data)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Invalid vendor'})
        else:
            return Response({'message': 'Subscription is out of date'})

    
    def delete(self, request, product_id):
        product = self.get_object(product_id)
        vendor = get_object_or_404(VendorProfile, user=request.user)
        if vendor.subscription_expires_at is not None and vendor.subscription_expires_at < timezone.now():
            vendor.unsubscripe()
        if vendor.is_subscriped():
            if vendor.vendor_id == product.vendor_identity:
                product.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': 'Invalid vendor'})
        else:
            return Response({'message': 'Subscription is out of date'})
        

class ProductImageView(APIView):
    def delete(self, request, product_id, image_id):
        product = get_object_or_404(Product, id=product_id)
        image = product.images.get(id=image_id)
        image.delete()
        return Response(status= status.HTTP_204_NO_CONTENT)
    

class OrderProductView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        serializer = ProductSerializer(product)
        cache_key = f'user_{request.user.id}_order_for_{product_id}_cache_key'
        quantity = cache.get(cache_key)
        total_price = int(product.discounted_price) * int(quantity)
        data = {
            'product': serializer.data,
            'total_price': total_price,
            'quantity': quantity
        }
        return Response(data)
    
    
    def post(self, request, product_id):
        serializer = OrderDetailSerializer(data=request.data)
        product = get_object_or_404(Product, id=product_id)
        name = product.product_name
        price = product.discounted_price
        order_image = ProductImage.objects.filter(product=product).first()
        vendor_name = product.vendor_name
        vendor_id = product.vendor_identity
        cache_key = f'user_{request.user.id}_order_for_{product_id}_cache_key'
        quantity = cache.get(cache_key)
        if quantity == None:
            return Response({'message': 'cache timeout'})
        total_sum = price* int(quantity)
        percentage = total_sum * 0.02
        percentage_sum = total_sum + percentage 

        vendor = VendorProfile.objects.get(vendor_id = vendor_id)
        vendor_account_number = vendor.account_number
        vendor_wallet = get_object_or_404(Wallet,account_number=vendor_account_number)
        customer_wallet = get_object_or_404(Wallet,user=request.user)
    
        if serializer.is_valid(): 
            transfer = Transaction(vendor_wallet, customer_wallet, percentage_sum)
            if 'pin' in request.data:
                if check_password(request.data['pin'], request.user.transaction_pin):
                    if transfer.pay():
                        
                        order = OrderDetail.objects.create(user = request.user, order_id = uuid.uuid4(), order_otp_token = secrets.token_hex(4), first_name=request.data['first_name'], last_name=request.data['last_name'], address=request.data['address'], phone_number=request.data['phone_number'], email_address=request.data['email_address'], 
                                                            product_name=name, product_image = order_image.image, product_price=price, vendor_name=vendor_name, vendor_id =vendor_id, product_quantity=quantity, total_price = total_sum)      
                        order.save()
                        pending_payment = Pending.objects.create(product_id=product_id, quantity=quantity, order_id=order.order_id, account_number=customer_wallet.account_number, otp_token=order.order_otp_token, amount=total_sum)
                        pending_payment.save()
                        transaction_percentage = get_object_or_404(TransactionPercentage, name='Transaction percentage')
                        transaction_percentage.balance += Decimal(percentage)
                        transaction_percentage.save()
                        transaction_history = TransactionHistory.objects.create(user=request.user, transaction='Debit', transaction_type='Order', transaction_amount=total_sum, recipient=vendor_name, sender=str(customer_wallet.first_name)+' '+str(customer_wallet.last_name), product_name=name, product_quantity=quantity)
                        transaction_history.save()
                        order_serializer = OrderDetailSerializer(order)                
                        product.stock -= int(quantity)
                        product.quantity_sold += int(quantity)
                        product.save()
                        
                        return Response(order_serializer.data, status=status.HTTP_201_CREATED)
                    else:      
                        return Response({'message': 'insufficient funds'})
                else:
                    return Response({'message': 'Invalid pin'})
            else:
                return Response({'message': 'Transaction pin required'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class VendorPayment(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def post(self, request):
        order_id = request.data['order_id']
        otp_token = request.data['otp_token']
        current_vendor = get_object_or_404(VendorProfile, user=request.user)
        if current_vendor.subscription_expires_at is not None and current_vendor.subscription_expires_at < timezone.now():
            current_vendor.unsubscripe()
        if current_vendor.is_subscriped():
            pending_funds = Pending.objects.filter(order_id=order_id).first()
            if pending_funds:
                order = OrderDetail.objects.filter(order_id=order_id).first()
                
                if str(current_vendor.vendor_id) == order.vendor_id:
                    if otp_token == pending_funds.otp_token:
                
                        wallet = get_object_or_404(Wallet, user=request.user)
                        wallet.funds += pending_funds.amount
                        wallet.save()
                        transaction_history = TransactionHistory.objects.create(user=request.user, transaction='Credit', transaction_type='Order', transaction_amount=pending_funds.amount, product_name=order.product_name, sender=order.order_id, product_quantity=order.product_quantity)
                        transaction_history.save()
                        order.payment_status = 'Paid and Confirmed'
                        order.order_status = 'Delivered'
                        order.save()
                        pending_funds.delete()
                        return Response({'message': 'Your account has been credited successfully'})
                    else:
                        return Response({'message': 'invalid order id or otp token'})   
                else:
                    return Response({'message': 'invalid vendor identity'})       
            else:
                return Response({'message': 'invalid order id or otp token'})
        else:
            return Response({'message': 'Subscription is out of date'})




class WalletView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        wallet = get_object_or_404(Wallet, user=request.user)
        acct_number = wallet.account_number
        pending = Pending.objects.filter(account_number=acct_number)
        if pending:
            for items in pending:
                if items.reverse_payment:
                    wallet.funds += items.amount
                    wallet.save()
                    transaction_history = TransactionHistory.objects.create(user=request.user, transaction='Credit', transaction_type='Reverse payment', transaction_amount=items.amount, sender='Safemall reverse payment', recipient=str(wallet.first_name)+' '+str(wallet.last_name) )
                    transaction_history.save()
                    order = get_object_or_404(OrderDetail, order_id=items.order_id)
                    order.payment_status = 'Payment Reversed'
                    order.order_status = 'Cancelled'
                    order.save()
                    product = Product.objects.filter(id=items.product_id).first()
                    if product:
                        product.stock += items.quantity
                        product.quantity_sold -= items.quantity
                        product.save()
                    pending.delete()
                    wallet_serializer = WalletSerializer(wallet)
                    data = {
                        'message' :'You have been refunded successfully',
                        'wallet' : wallet_serializer.data
                    }
                    return Response(data)
        else:
            serializer = WalletSerializer(wallet)
            return Response(serializer.data)




class TransactionHistoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transaction_history = TransactionHistory.objects.filter(user=request.user).order_by('-created_at')
        if transaction_history:
            serializer = TransactionSerializer(transaction_history, many=True)
            return Response(serializer.data)
        else:
            return Response({'message': 'No Transactions Yet'})





class TranferView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request):
        account_number = request.GET.get('account_number')
        if account_number:
            account = Wallet.objects.filter(account_number=account_number).first()
            if account:
                serializer = TransferWalletSerializer(account)
                cache_key = f'user_{request.user.id}_cache_key'
                cache.set(cache_key,account.account_number,3600)
                return Response(serializer.data)
            else:
                return Response({'message': 'Input a valid account number'})
        else:
            return Response({'message': 'Input an account number'})


    def post(self, request):
        amount = request.data['amount']
        pin = request.data['pin']
        sender = get_object_or_404(Wallet, user=request.user)
        cache_key = f'user_{request.user.id}_cache_key'
        account_number = cache.get(cache_key)
        if account_number:
            if request.user.transaction_pin == '':
                return Response({'message':'You have not set your transaction pin'})
            if pin == request.user.transaction_pin:
                recipient = get_object_or_404(Wallet, account_number=account_number)
                if recipient.user != request.user:
                    transfer = TransferFunds(sender, recipient, amount)
                    if transfer.payment():
                        percentage = Decimal(amount) * Decimal(0.03)
                        transaction_percentage = get_object_or_404(TransactionPercentage, name='Transaction percentage')
                        transaction_percentage.balance += percentage
                        transaction_percentage.save()
                        sender_transaction_history = TransactionHistory.objects.create(user=request.user, transaction='Debit', transaction_type='Transfer', transaction_amount=amount,
                                                                                sender=str(sender.first_name)+' '+str(sender.last_name), recipient=str(recipient.first_name)+' '+str(recipient.last_name))
                        sender_transaction_history.save()

                        recipient_transaction_history = TransactionHistory.objects.create(user=recipient.user, transaction='Credit', transaction_type='Transfer', transaction_amount=amount,
                                                                                sender=str(sender.first_name)+' '+str(sender.last_name), recipient=str(recipient.first_name)+' '+str(recipient.last_name))
                        recipient_transaction_history.save()
                        serializer = TransactionSerializer(sender_transaction_history)
                        data = {
                            'message': 'Transaction done successfully',
                            'receipt': serializer.data
                        }
                        return Response(data)
                    else:
                        return Response({'message': 'Insufficient fund'})
                else:
                    return Response({'message': 'Invalid transaction'})
            else:
                return Response({'message': 'Invalid pin'})
        else:
            return Response({'message': 'Cache timeout'})




class ClothesPageView(APIView):

    #@method_decorator(cache_page(60 * 15, key_prefix='product_category'))
    def get(self, request):
        clothpage = Product.objects.filter(product_category='clothes').order_by('-uploaded_at')
        clothserializer = ProductSerializer(clothpage, many=True)
        return Response(clothserializer.data)
    


class FoodPageView(APIView):

    #@method_decorator(cache_page(60 * 15, key_prefix='product_category'))
    def get(self, request):
        foodpage = Product.objects.filter(product_category='food').order_by('-uploaded_at')
        foodserializer = ProductSerializer(foodpage, many=True)
        return Response(foodserializer.data)
    

class FootwearsPageView(APIView):

    #@method_decorator(cache_page(60 * 15, key_prefix='product_category'))
    def get(self, request):
        footwearpage = Product.objects.filter(product_category='footwears').order_by('-uploaded_at')
        footwearserializer = ProductSerializer(footwearpage, many=True)
        return Response(footwearserializer.data)
    

class AccessoriesPageView(APIView):

    #@method_decorator(cache_page(60 * 15, key_prefix='product_category'))
    def get(self, request):
        accessoriespage = Product.objects.filter(product_category='accessories').order_by('-uploaded_at')
        accessoriesserializer = ProductSerializer(accessoriespage, many=True)
        return Response(accessoriesserializer.data)
    

class BeautyPageView(APIView):

    #@method_decorator(cache_page(60 * 15, key_prefix='product_category'))
    def get(self, request):
        beautypage = Product.objects.filter(product_category='beauty').order_by('-uploaded_at')
        beautyserializer = ProductSerializer(beautypage, many=True)
        return Response(beautyserializer.data)
    

class HouseholdPageView(APIView):

    #@method_decorator(cache_page(60 * 15, key_prefix='product_category'))
    def get(self, request):
        householdpage = Product.objects.filter(product_category='household').order_by('-uploaded_at')
        householdserializer = ProductSerializer(householdpage, many=True)
        return Response(householdserializer.data)
    

class NewArrivalsView(APIView):

    #@method_decorator(cache_page(60 * 15, key_prefix='new_arrivals'))
    def get(self, request):
        total = Product.objects.count() - 3
        new_arrivals = Product.objects.all().order_by('-uploaded_at')[:20]
        serializer = ProductSerializer(new_arrivals, many=True)
        return Response(serializer.data)
    

class ExploreView(APIView):

    #@method_decorator(cache_page(60 * 30, key_prefix='explore'))
    #@method_decorator(vary_on_headers)
    def get(self, request):
        max_id = VendorProfile.objects.values_list('id', flat=True)
        random_ids = random.sample(list(max_id), min(20, len(max_id)))
        random_data = VendorProfile.objects.filter(id__in=random_ids)
        vendor_serializer = VendorSerializer(random_data, many=True)
        return Response(vendor_serializer.data)
    

class FeaturedProductView(APIView):

    #@method_decorator(cache_page(60 * 30, key_prefix='featured_products'))
    #@method_decorator(vary_on_headers)
    def get(self, request):
        max_id = Product.objects.values_list('id', flat=True)
        random_ids = random.sample(list(max_id), min(25, len(max_id)))
        random_data = Product.objects.filter(id__in=random_ids)
        product_serializer = ProductSerializer(random_data, many=True)
        return Response(product_serializer.data)


class VendorPageView(APIView):

    #@method_decorator(cache_page(60 * 30, key_prefix='vendor_page'))
    def get(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, vendor_id=vendor_id)
        product = Product.objects.filter(vendor_identity=vendor_id).order_by('-uploaded_at')
        value = ProductReview.objects.filter(vendor_id=vendor_id).aggregate(Avg('rating'))['rating__avg']
        vendor_rating = 1.0
        if value is not None:
            vendor_rating = round(value, 1)
        vendor_serializer = VendorSerializer(vendor)
        product_serializer = ProductSerializer(product, many=True)
        data = {
            'vendor_data': vendor_serializer.data,
            'vendor_rating': vendor_rating,
            'product_data': product_serializer.data            
        }
        return Response(data)
    


class ProfileDetails(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    
    def put(self, request):
        user = request.user
        data = request.data.copy()
        data.pop('profile_image', None)
        image = request.FILES.getlist('profile_image')
        if image:
            image = image[0]
        serializer = UserSerializer(user, data=data)
        
        if serializer.is_valid():
            if image:
                user.profile_image = image
                user.save()
            serializer.save()
            buyer = get_object_or_404(BuyerProfile, user=request.user)
            buyer.first_name = user.first_name
            buyer.last_name = user.last_name
            buyer.phone_number = user.phone_number
            buyer.save()
            reviews = ProductReview.objects.filter(user=request.user)
            for review in reviews:
                review.first_name = user.first_name
                review.last_name = user.last_name
                review.image = user.profile_image
                review.save()
            wallet = get_object_or_404(Wallet, user=request.user)
            wallet.first_name = user.first_name
            wallet.last_name = user.last_name
            wallet.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
          
    
class SearchProduct(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search_query = request.GET.get('search')
        if search_query is not None:
            product = Product.objects.filter(product_name__icontains=search_query) | Product.objects.filter(vendor_name__icontains=search_query)
            serializer = ProductSerializer(product, many=True)
            return Response(serializer.data)
        else:
            return Response({'message': 'Please provide a search query'})



class ProductReviewView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #@method_decorator(cache_page(60*30, key_prefix='product_reviews'))
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        review = ProductReview.objects.filter(product=product).order_by('-created_at')
        value = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        rating_avg = 0.0
    
        if value is not None:
            rating_avg = round(value, 1)
            serializer = ProductReviewSerializer(review, many=True)
            total_number = review.count()
            data = {
                'reviews': serializer.data,
                'total': total_number,
                'average rating': rating_avg
            }
            return Response(data)
        else:
            return Response({'message': []})
        
        
            

    def post(self, request, product_id):
        user = request.user
        image = user.profile_image
        first_name = user.first_name
        last_name = user.last_name
        product = get_object_or_404(Product, id=product_id)
        vendor_id = product.vendor_identity
        review = ProductReview.objects.create(user=user, product=product, vendor_id=vendor_id, first_name=first_name, last_name=last_name, image=image, rating=request.data['rating'], review=request.data['review'])
        review.save()

        value = round(ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'], 1)
        product.average_rating = value
        product.save()
        serializer = ProductReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class VendorOrderView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        vendor = get_object_or_404(VendorProfile, user=user)
        vendor_id = vendor.vendor_id
        if vendor.subscription_expires_at is not None and vendor.subscription_expires_at < timezone.now():
            vendor.unsubscripe()
        if vendor.is_subscriped():
            vendor_order = OrderDetail.objects.filter(vendor_id=vendor_id).order_by('-created_at')
            if vendor_order:
                serializer = OrderDetailForVendorsSerializer(vendor_order, many=True)
                return Response(serializer.data)
            else:
                return Response({'message': 'No order yet'})
        else:
            return Response({'message': 'Subscription is out of date'})
       
        

class BuyerOrderView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        order = OrderDetail.objects.filter(user=user).order_by('-created_at')
        if order:
            serializer = OrderDetailSerializer(order, many=True)
            return Response(serializer.data)
        else:
            return Response({'message': 'You have made no order yet'})
        

class InventoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        vendor = get_object_or_404(VendorProfile, user=user)
        vendor_id = vendor.vendor_id
        if vendor.subscription_expires_at is not None and vendor.subscription_expires_at < timezone.now():
            vendor.unsubscripe()
        if vendor.is_subscriped():
            product = Product.objects.filter(vendor_identity=vendor_id).order_by('-uploaded_at')
            if product:
                serializer = ProductSerializer(product, many=True)
                return Response(serializer.data)
            else:
                return Response({'message': []})
        else:
            return Response({'message': 'Subscription is out of date'})
