from django.shortcuts import render
from rest_framework.response import Response
from django.conf import settings
from rest_framework.views import APIView
import firebase_admin
from firebase_admin import credentials, messaging, exceptions
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.http import Http404
from django.db.models.functions import Lower
from .serializers import UserSerializer, BuyerSerializer, VendorSerializer, ProductSerializer,OrderDetailForVendorsSerializer, OrderDetailSerializer, ProductImageSerializer, ProductReviewSerializer, WalletSerializer, TransactionSerializer, TransferWalletSerializer
from .models import (BuyerProfile, TransactionOtpTokenGenerator, VendorProfile, Product,TransactionPercentage , EmailOtpTokenGenerator,
                     OrderDetail, ProductImage, ProductReview, OtpTokenGenerator, Pending, Wallet, TransactionHistory)
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models.fields.files import ImageFieldFile
from django.db import transaction
from .paystack import Paystack
from rest_framework import status, generics
from .transaction import Transaction, TransferFunds
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
import secrets
from django.core.mail import send_mail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.views.decorators.vary import vary_on_headers
import random 
from decimal import Decimal
import uuid
from django.core.cache import cache
from django.db.models import Avg
from django.utils import timezone
import requests
# Create your views here.

# cred = credentials.Certificate('path/to/firebase_credentials.json')
#firebase_admin.initialize_app(cred)

#signup API for registering buyers
class BuyerSignupApi(APIView):
    
    
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        User = get_user_model()
        
        if User.objects.filter(email=request.data['email']).exists():
            return Response({'message': 'email already exists'})
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
                return Response({'message': 'email already exists'})
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
        data = {
            'firebase_token': request.user.firebase_token,
            'vendor': Vendorstore.data
        }
        return Response(data, status=status.HTTP_201_CREATED)
    
    def put(self, request):
        user = get_object_or_404(VendorProfile, user=request.user)
        serializer = VendorSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            if request.data['business_name']:
                products = Product.objects.filter(vendor_identity = user.vendor_id)
                if products:
                    for product in products:
                        product.vendor_name = request.data['business_name']
                        product.save()
                reviews = ProductReview.objects.filter(vendor_id=user.vendor_id)
                if reviews:
                    for items in reviews:
                        items.vendor_name = request.data['business_name']
                        items.save()
            if request.data['profile_image']:
                products = Product.objects.filter(vendor_identity = user.vendor_id)
                for product in products:
                    product.vendor_image = request.data['profile_image']
                    product.save()
            data = {
            'firebase_token': request.user.firebase_token,
            'vendor': serializer.data
        }
            return Response(data, status=status.HTTP_200_OK)
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
                data = {
            
            'message': 'pin set successfully'
        }
                return Response(data)
            else:
                return Response({'message': 'please input a valid pin'})
        else:
            return Response({'message': 'pin is required'})


class SubscriptionView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vendor = get_object_or_404(VendorProfile, user=request.user)
        vendor.subscripe_for_two_hours()
        data = {
            
            'message': 'you are subscribed for 2 hours'
        }
        return Response(data)



class ProductUploadView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    
    def post(self, request):
        user = request.user
        vendor = get_object_or_404(VendorProfile, user=user)
        if vendor.subscription_expires_at is not None and vendor.subscription_expires_at < timezone.now():
            vendor.unsubscripe()
        if vendor.is_subscriped():
            if user.email_verified:
                name = vendor.business_name
                identity = vendor.vendor_id
                vendor_image = vendor.profile_image
                serializer = ProductSerializer(data=request.data)
                if vendor.business_name == '':
                    return Response({"message": "you haven't set up your store"})
                else:
                    if int(request.data['discounted_amount']) > int(request.data['product_price']):
                        return Response({'message': 'product discount cannot be greater than product price'})
                    else:
                        if serializer.is_valid():
                            product = Product.objects.create(vendor=vendor, product_name=request.data['product_name'], vendor_image=vendor_image, discounted_amount=request.data['discounted_amount'], stock=request.data['stock'], product_description=request.data['product_description'], product_category=request.data['product_category'], vendor_name=name,
                                                            vendor_identity=identity, product_price=request.data['product_price'],school=user.school)
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
                            data = {
                                'firebase_token': request.user.firebase_token,
                                'data': product_serializer.data
                                }
                            return Response(data , status=status.HTTP_201_CREATED)
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'email not verified'})                
        else:
            return Response({'message': 'subscription is out of date'})
        


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
        data = {
            'firebase_token': request.user.firebase_token,
            'data': serializer.data
        }
        return Response(data)
        

       
    def post(self, request, product_id):
        product = self.get_object(product_id)
        vendor = VendorProfile.objects.filter(user=request.user).first()
        if vendor:
            if product.vendor_identity == vendor.vendor_id:
                return Response({'message': 'you cannot order your own product'})
            else:
                quantity = int(request.data['quantity'])
                serializer = ProductSerializer(product)
                if int(quantity) < int(product.stock):
                    cache_key = f'user_{request.user.id}_order_for_{product_id}_cache_key'
                    cache.set(cache_key, quantity, 3600)
                    data = {
                        'firebase_token': request.user.firebase_token,
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
                    'firebase_token': request.user.firebase_token,
                    'product': serializer.data,
                    'quantity': quantity
                }
                return Response(data)
            else:
                return Response({'message': 'product stock is not up to the quantity inputted'})            
        

    @transaction.atomic        
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
                        product.percentage_discount = round(percentage)
                        product.discounted_price = discounted_price
                        product.updated_at = timezone.now()
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
                        data = {
                            'firebase_token': request.user.firebase_token,
                            'message': 'product updated',
                            'data': serializer.data
                        }
                        return Response(data)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'invalid vendor'})
        else:
            return Response({'message': 'subscription is out of date'})

    
    def delete(self, request, product_id):
        product = self.get_object(product_id)
        vendor = get_object_or_404(VendorProfile, user=request.user)
       
        if vendor.vendor_id == product.vendor_identity:
            product.delete()
            data = {
                'message': 'product deleted'
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'invalid vendor'})

        

class ProductImageView(APIView):
    def delete(self, request, product_id, image_id):
        product = get_object_or_404(Product, id=product_id)
        image = product.images.get(id=image_id)
        image.delete()
        data = {
                'message': 'image deleted'
            }
        return Response(data, status= status.HTTP_204_NO_CONTENT)
    

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
            'firebase_token': request.user.firebase_token,
            'product': serializer.data,
            'total_price': total_price,
            'quantity': quantity
        }
        return Response(data)
    
    @transaction.atomic
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
            
            if 'pin' in request.data:
                if check_password(request.data['pin'], request.user.transaction_pin):
                    if request.user.email_verified:
                        transfer = Transaction(vendor_wallet, customer_wallet, percentage_sum)
                        if transfer.pay():
                            
                            order = OrderDetail.objects.create(user = request.user, product_id = product.id, order_id = uuid.uuid4(), order_otp_token = secrets.token_hex(4), first_name=request.data['first_name'], last_name=request.data['last_name'], address=request.data['address'], phone_number=request.data['phone_number'], email_address=request.data['email_address'], 
                                                                product_name=name, product_image = order_image.image, product_price=price, vendor_name=vendor_name, vendor_id =vendor_id, product_quantity=quantity, total_price = total_sum)      
                            order.save()
                            pending_payment = Pending.objects.create(product_id=product_id, quantity=quantity, order_id=order.order_id, account_number=customer_wallet.account_number, otp_token=make_password(order.order_otp_token), amount=total_sum)
                            pending_payment.save()
                            transaction_percentage = get_object_or_404(TransactionPercentage, name='Transaction percentage')
                            transaction_percentage.balance += Decimal(percentage)
                            transaction_percentage.save()
                            transaction_history = TransactionHistory.objects.create(user=request.user, transaction_id=str(uuid.uuid4().int)[:20], transaction='Debit', transaction_type='Order', transaction_amount=total_sum, recipient=vendor_name, sender=str(customer_wallet.first_name)+' '+str(customer_wallet.last_name), product_name=name, product_quantity=quantity)
                            transaction_history.save()
                            order_serializer = OrderDetailSerializer(order)                
                            product.stock -= int(quantity)
                            product.quantity_sold += int(quantity)
                            product.save()
                            cache.delete(cache_key)

                            User = get_user_model()
                            vendor_user_model = get_object_or_404(User, email=vendor.vendor_email)
                            vendor_token = vendor_user_model.fcm_token

                            if vendor_token:
                               
                               message = messaging.Message(
                                    notification=messaging.Notification(
                                        title=f'{vendor_user_model.first_name}, you are making sales!',
                                        body=f'You have a pending order from {request.user.first_name} {request.user.last_name}'
                                    ),
                                    token=vendor_token,

                                 )
                               try:
                                    messaging.send(message)
                               except exceptions.FirebaseError as e:
                                    if 'NotRegistered' in str(e) or 'InvalidRegistration' in str(e):
                                        vendor_token = ''
                                        vendor_user_model.save() 
    
                            data = {
                                'firebase_token': request.user.firebase_token,
                                'data': order_serializer.data
                            }
                            return Response(data, status=status.HTTP_201_CREATED)
                        else:      
                            return Response({'message': 'insufficient funds'})
                    else:
                        return Response({'message': 'email not verified'})
                else:
                    return Response({'message': 'invalid pin'})
            else:
                return Response({'message': 'transaction pin required'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class VendorPayment(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
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
                    if check_password(otp_token, pending_funds.otp_token):
                
                        wallet = get_object_or_404(Wallet, user=request.user)
                        wallet.funds += pending_funds.amount
                        wallet.save()
                        transaction_history = TransactionHistory.objects.create(user=request.user, transaction_id=str(uuid.uuid4().int)[:20], transaction='Credit', transaction_type='Order', transaction_amount=pending_funds.amount, product_name=order.product_name, sender=order.order_id, product_quantity=order.product_quantity)
                        transaction_history.save()
                        order.payment_status = 'Paid and Confirmed'
                        order.order_status = 'Delivered'
                        order.save()
                        pending_funds.delete()
                        data = {
                            'firebase_token': request.user.firebase_token,
                            'message': 'your account has been credited successfully'
                        }
                        return Response(data)
                    else:
                        return Response({'message': 'invalid order id or otp token'})   
                else:
                    return Response({'message': 'invalid transaction'})       
            else:
                return Response({'message': 'invalid order id or otp token'})
        else:
            return Response({'message': 'subscription is out of date'})




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
                    transaction_history = TransactionHistory.objects.create(user=request.user, transaction='Credit', transaction_type='Reverse payment', transaction_id=str(uuid.uuid4().int)[:20], transaction_amount=items.amount, sender='Safemall reverse payment', recipient=str(wallet.first_name)+' '+str(wallet.last_name) )
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
                    items.delete()
            wallet_serializer = WalletSerializer(wallet)
            data = {
                'data': wallet_serializer.data
            }
            return Response(data)
        else:
            serializer = WalletSerializer(wallet)
            data = {
                'data': serializer.data
            }
            return Response(data)




class TransactionHistoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transaction_history = TransactionHistory.objects.filter(user=request.user).order_by('-created_at')
        if transaction_history:
            serializer = TransactionSerializer(transaction_history, many=True)
            data = {
                'data': serializer.data
            }
            return Response(data)
        else:
            data = {
                'data': []
            }
            return Response(data)





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
                data = {
                'data': serializer.data
            }
                return Response(data)
            else:
                return Response({'message': 'input a valid account number'})
        else:
            return Response({'message': 'input an account number'})

    @transaction.atomic
    def post(self, request):
        amount = request.data['amount']
        pin = request.data['pin']
        sender = get_object_or_404(Wallet, user=request.user)
        cache_key = f'user_{request.user.id}_cache_key'
        account_number = cache.get(cache_key)
        if account_number:
            if request.user.transaction_pin == '':
                return Response({'message':'you have not set your transaction pin'})
            if check_password(pin, request.user.transaction_pin):
                recipient = get_object_or_404(Wallet, account_number=account_number)
                if recipient.user != request.user:
                    if request.user.email_verified:
                        transfer = TransferFunds(sender, recipient, amount)
                        if transfer.payment():
                            sender_transaction_history = TransactionHistory.objects.create(user=request.user, transaction_id=str(uuid.uuid4().int)[:20], transaction='Debit', transaction_type='Transfer', transaction_amount=amount,
                                                                                    sender=str(sender.first_name)+' '+str(sender.last_name), recipient=str(recipient.first_name)+' '+str(recipient.last_name))
                            sender_transaction_history.save()

                            recipient_transaction_history = TransactionHistory.objects.create(user=recipient.user, transaction_id=str(uuid.uuid4().int)[:20], transaction='Credit', transaction_type='Transfer', transaction_amount=amount,
                                                                                    sender=str(sender.first_name)+' '+str(sender.last_name), recipient=str(recipient.first_name)+' '+str(recipient.last_name))
                            recipient_transaction_history.save()
                            serializer = TransactionSerializer(sender_transaction_history)
                            cache.delete(cache_key)
                            data = {
                                'message': 'transaction done successfully',
                                'receipt': serializer.data
                            }

                            User = recipient.user
                            recipient_token = User.fcm_token
                            if recipient_token:
                                message = messaging.Message(
                                    notification=messaging.Notification(
                                        title='Credit Alert!',
                                        body=f'Your account has been credited with ₦{amount} by  {request.user.first_name} {request.user.last_name}'
                                    ),
                                    token=recipient_token,

                                )
                                try:
                                    messaging.send(message)
                                except exceptions.FirebaseError as e:
                                    if 'NotRegistered' in str(e) or 'InvalidRegistration' in str(e):
                                        recipient_token = ''
                                        User.save()
                            return Response(data)
                        else:
                            return Response({'message': 'insufficient fund'})
                    else:
                        return Response({'message': 'email not verified'})
                else:
                    return Response({'message': 'invalid transaction'})
            else:
                return Response({'message': 'invalid pin'})
        else:
            return Response({'message': 'cache timeout'})




class ClothesPageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #@method_decorator(cache_page(60 * 15, key_prefix='product_category'))
    def get(self, request):
        user = request.user
        clothpage = Product.objects.filter(product_category='clothes').order_by('-uploaded_at')
        clothserializer = ProductSerializer(clothpage, many=True)
        data = {
                'firebase_token': request.user.firebase_token,
                'data': clothserializer.data
            }
        return Response(data)
    


class FoodPageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #@method_decorator(cache_page(60 * 15, key_prefix='product_category'))
    def get(self, request):
        user = request.user
        foodpage = Product.objects.filter(product_category='food').order_by('-uploaded_at')
        foodserializer = ProductSerializer(foodpage, many=True)
        data = {
                'firebase_token': request.user.firebase_token,
                'data': foodserializer.data
            }
        return Response(data)
    

class FootwearsPageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #@method_decorator(cache_page(60 * 15, key_prefix='product_category'))
    def get(self, request):
        user = request.user
        footwearpage = Product.objects.filter(product_category='footwears').order_by('-uploaded_at')
        footwearserializer = ProductSerializer(footwearpage, many=True)
        data = {
                'firebase_token': request.user.firebase_token,
                'data': footwearserializer.data
            }
        return Response(data)
    

class AccessoriesPageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #@method_decorator(cache_page(60 * 15, key_prefix='product_category'))
    def get(self, request):
        user = request.user
        accessoriespage = Product.objects.filter(product_category='accessories').order_by('-uploaded_at')
        accessoriesserializer = ProductSerializer(accessoriespage, many=True)
        data = {
                'firebase_token': request.user.firebase_token,
                'data': accessoriesserializer.data
            }
        return Response(data)
    

class BeautyPageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #@method_decorator(cache_page(60 * 15, key_prefix='product_category'))
    def get(self, request):
        user = request.user
        beautypage = Product.objects.filter(product_category='beauty').order_by('-uploaded_at')
        beautyserializer = ProductSerializer(beautypage, many=True)
        data = {
                'firebase_token': request.user.firebase_token,
                'data': beautyserializer.data
            }
        return Response(data)
    

class HouseholdPageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #@method_decorator(cache_page(60 * 15, key_prefix='product_category'))
    def get(self, request):
        user = request.user
        householdpage = Product.objects.filter(product_category='household').order_by('-uploaded_at')
        householdserializer = ProductSerializer(householdpage, many=True)
        data = {
                'firebase_token': request.user.firebase_token,
                'data': householdserializer.data
            }
        return Response(data)
    

class NewArrivalsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #@method_decorator(cache_page(60 * 15, key_prefix='new_arrivals'))
    def get(self, request):
        user = request.user
        total = Product.objects.count() - 3
        new_arrivals = Product.objects.all().order_by('-uploaded_at')[:20]
        serializer = ProductSerializer(new_arrivals, many=True)
        data = {
                'firebase_token': request.user.firebase_token,
                'data': serializer.data
            }
        return Response(data)
    

class ExploreView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #@method_decorator(cache_page(60 * 30, key_prefix='explore'))
    #@method_decorator(vary_on_headers)
    def get(self, request):
        max_id = VendorProfile.objects.values_list('id', flat=True)
        random_ids = random.sample(list(max_id), min(20, len(max_id)))
        random_data = VendorProfile.objects.filter(id__in=random_ids)
        vendor_serializer = VendorSerializer(random_data, many=True)
        data = {
            'firebase_token': request.user.firebase_token,
            'message': 'product fetched successfully',
            'data': vendor_serializer.data
        }
        return Response(data)
    

class FeaturedProductView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #@method_decorator(cache_page(60 * 30, key_prefix='featured_products'))
    #@method_decorator(vary_on_headers)
    def get(self, request):
        max_id = Product.objects.values_list('id', flat=True)
        random_ids = random.sample(list(max_id), min(25, len(max_id)))
        random_data = Product.objects.filter(id__in=random_ids)
        product_serializer = ProductSerializer(random_data, many=True)
        data = {
            'firebase_token': request.user.firebase_token,
            'message': 'Products fetched successfully',
            'data':product_serializer.data
        }
        return Response(data)


class VendorPageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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
            'firebase_token': request.user.firebase_token,
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
        data = {
            'firebase_token': request.user.firebase_token,
            'data': serializer.data 
        }
        return Response(data)
    
    @transaction.atomic
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
            buyer = BuyerProfile.objects.filter(user=request.user).first()
            if buyer:
                buyer.first_name = user.first_name
                buyer.last_name = user.last_name
                buyer.phone_number = user.phone_number
                buyer.save()
            vendor = VendorProfile.objects.filter(user=user).first()
            if vendor:
                products = Product.objects.filter(vendor=vendor)
                if products:
                    for product in products:
                        product.school = user.school
                        product.save()
            reviews = ProductReview.objects.filter(user=request.user)
            if reviews:
                for review in reviews:
                    review.first_name = user.first_name
                    review.last_name = user.last_name
                    review.image = user.profile_image
                    review.save()
            wallet = get_object_or_404(Wallet, user=request.user)
            wallet.first_name = user.first_name
            wallet.last_name = user.last_name
            wallet.save()
            data = {
                'firebase_token': request.user.firebase_token,
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
          
    
class SearchProduct(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search_query = request.GET.get('search')
        if search_query is not None:
            product = Product.objects.filter(product_name__icontains=search_query).order_by(Lower('product_name'))  or Product.objects.filter(vendor_name__icontains=search_query).order_by(Lower('product_name')) 
            serializer = ProductSerializer(product, many=True)
            data = {
                'data': serializer.data
            }
            return Response(data)
        else:
            data = {
                'data': []
            }
            return Response(data)



class ProductReviewView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #@method_decorator(cache_page(60*30, key_prefix='product_reviews'))
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product_reviews = ProductReview.objects.filter(is_deleted = False)
        review = product_reviews.filter(product=product).order_by('-created_at')
        value = ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        rating_avg = 0.0
    
        if value is not None:
            rating_avg = round(value, 1)
            serializer = ProductReviewSerializer(review, many=True)
            total_number = review.count()
            data = {
                'firebase_token': request.user.firebase_token,
                'reviews': serializer.data,
                'total': total_number,
                'average rating': rating_avg
            }
            return Response(data)
        else:
            data = {
                'message': []
            }
            return Response(data)
        


        
class PostProductReviewView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id, order_id):
        user = request.user
        image = user.profile_image
        first_name = user.first_name
        last_name = user.last_name
        order = OrderDetail.objects.filter(order_id = order_id).first()
        product = get_object_or_404(Product, id=product_id)
        product_image = ProductImage.objects.filter(product=product).first()
        vendor_id = product.vendor_identity
        if not ProductReview.objects.filter(order_pk=order.id).exists():
            review = ProductReview.objects.create(user=user, order=order, order_pk=order.id, product=product, product_name=product.product_name, product_image=product_image.image, vendor_name=product.vendor_name, vendor_id=vendor_id, first_name=first_name, last_name=last_name, image=image, rating=request.data['rating'], review=request.data['review'])
            review.save()

            value = round(ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'], 1)
            product.average_rating = value
            product.save()
            serializer = ProductReviewSerializer(review)
            data = {
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = {
                'data': 'You have already added a review for this order'
            }
            return Response(data)
    

class UpdateProductReviewView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_pk, product_id):
        rating = request.data.get('rating', 0)
        review = request.data.get('review', 0)
        user_product_review = ProductReview.objects.filter(order_pk=order_pk).first()
        product = get_object_or_404(Product, id=product_id)
        if rating and review != 0:
            user_product_review.rating = rating
            user_product_review.review = review
            user_product_review.edited_at = timezone.now()
            user_product_review.save()
            value = round(ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'], 1)
            product.average_rating = value
            product.save()
            data = {
                'data': 'product review updated'
            }
            return Response(data)
        elif rating != 0 and review == 0:
            user_product_review.rating = rating
            user_product_review.edited_at = timezone.now()
            user_product_review.save()
            value = round(ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'], 1)
            product.average_rating = value
            product.save()
            data = {
                'data': 'product review updated'
            }
            return Response(data)
        elif review != 0 and rating == 0:
            user_product_review.review = review
            user_product_review.edited_at = timezone.now()
            user_product_review.save()
            data = {
                'data': 'product review updated'
            }
            return Response(data)
        else:
            data = {
                'data': 'rating or review required'
            }
            return Response(data)
        

    def delete(self, request, order_pk, product_id):
            user_product_review = ProductReview.objects.filter(order_pk=order_pk).first()

            user_product_review.is_deleted = True
            user_product_review.save()
            data = {
                'data': 'product review deleted'
            }
            return Response(data)
        



    
class UserReviewsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_reviews = ProductReview.objects.filter(is_deleted=False)
        personal_user_reviews =  user_reviews.filter(user=request.user).order_by('-created_at')  
        if personal_user_reviews:
            serializer = ProductReviewSerializer(user_reviews, many=True)
            data = {
                'data': serializer.data
            }
            return Response(data)
        else:
            data = {
                'data': []
                }
            return Response(data)    




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
                data = {
                'data': serializer.data
                        }
                return Response(data)
            else:
                data = {
                'data': 'no order yet'
                        }
                return Response(data)
        else:
            data = {
                'data': 'subscription is out of date'
                        }
            return Response(data)
       
        

class BuyerOrderView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        order = OrderDetail.objects.filter(user=user).order_by('-created_at')
        if order:
            serializer = OrderDetailSerializer(order, many=True)
            data = {
                'data': serializer.data
                        }
            return Response(data)
        else:
            data = {
                'data': []
                        }
            return Response(data)
        

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
                data = {
                    'firebase_token': request.user.firebase_token,
                    'message': 'Products fetched successfully',
                    'data':serializer.data}
                return Response(data)
            else:
                data = { 'firebase_token': request.user.firebase_token,
                            'message': 'no product(s) yet',
                                'data':[]
                                }
                return Response(data)
        else:
            data = {
                        'message': 'subscription is out of date',
                             'data':[]
                            }
            return Response(data)



class PasswordResetView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            otp = secrets.token_hex(3)
            otp_token = OtpTokenGenerator.objects.create(user=user, otp_token=make_password(otp), otp_expires_at=timezone.now() + timezone.timedelta(minutes=30))
            otp_token.save()


            subject = 'Password Reset'
            recipient = [user.email]
            sender = settings.EMAIL_HOST_USER
            html_content = f""" 
            <html>
            <head>

            </head>
            <body>
            <h1> Password Reset Email </h1>
            <p> Dear {user.first_name}, </p>
            <p> we received a request to reset your password for your safemall account. </p>
            <p> To verify your identity, we've generated a one-time password (OTP) code:
            <h1> {otp} </h1>
            <p> Please enter this code in the password reset page to proceed with resetting your password. </p>
            <p> This code is valid for 30 minutes. If you have any issues resetting your password, please contact our support team at safemall202@gmail.com.
            <p> For your security, we recommend choosing a strong and unique password. </p>
            <p>Best regards, </p>
            <p> Safemall </p>
            <img src='https://safemall.pythonanywhere.com/media/image/img_tmp_tag1740339581455_1.jpg'/>
            <body>
            </html>
"""

            send_mail(subject=subject, recipient_list=recipient, message='', from_email=sender,html_message=html_content)
            
            data = {
                'message': f'a password recovery code was sent to {user.email}'
            }
            return Response(data)
        except Exception:
            data = {
                'message': 'error sending email'
            }
            return Response(data)
        
        

class ResendOtpCodeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
            user = request.user
            try:
                otp = secrets.token_hex(3)
                otp_token = OtpTokenGenerator.objects.create(user=user, otp_token=make_password(otp), otp_expires_at=timezone.now() + timezone.timedelta(minutes=30))
                otp_token.save()

                subject = 'Password Reset'
                recipient = [user.email]
                sender = settings.EMAIL_HOST_USER
                html_content = f""" 
                <html>
                <head>

                </head>
                <body>
                <h1> Password Reset Email </h1>
                <p> Dear {user.first_name}, </p>
                <p> we received a request to reset your password for your safemall account. </p>
                <p> To verify your identity, we've generated a one-time password (OTP) code:
                <h1> {otp} </h1>
                <p> Please enter this code in the password reset page to proceed with resetting your password. </p>
                <p> This code is valid for 30 minutes. If you have any issues resetting your password, please contact our support team at safemall202@gmail.com.
                <p> For your security, we recommend choosing a strong and unique password. </p>
                <p>Best regards, </p>
                <p> Safemall </p>
                <img src='https://safemall.pythonanywhere.com/media/image/img_tmp_tag1740339581455_1.jpg'/>
                <body>
                </html>
    """

                send_mail(subject=subject, recipient_list=recipient, message='', from_email=sender,html_message=html_content)
                data = {
                    'message': f'a password reset code was sent to {user.email}' }
                return Response(data)
            except Exception:
                data = {
                    'message': 'error sending email'}
                return Response(data)


class ForgottenPasswordView(APIView):
    
    def get(self, request):
        User = get_user_model()
        email = request.data['email']
        user = User.objects.filter(email=email).first()
        if user:
            try:
                otp = secrets.token_hex(3)
                otp_token = OtpTokenGenerator.objects.create(user=user, otp_token=make_password(otp), otp_expires_at=timezone.now() + timezone.timedelta(minutes=30))
                otp_token.save()

                subject = 'Forgotten Password'
                recipient = [email]
                sender = settings.EMAIL_HOST_USER
                html_content = f""" 
                <html>
                <head>

                </head>
                <body>
                <h1> Password Reset Email </h1>
                <p> Dear {user.first_name}, </p>
                <p> we received a request to reset your password for your safemall account. </p>
                <p> To verify your identity, we've generated a one-time password (OTP) code:
                <h1> {otp} </h1>
                <p> Please enter this code in the password recovery page to proceed with resetting your password. </p>
                <p> This code is valid for 30 minutes. If you have any issues resetting your password, please contact our support team at safemall202@gmail.com.
                <p> For your security, we recommend choosing a strong and unique password. </p>
                <p>Best regards, </p>
                <p> Safemall </p>
                <img src='https://safemall.pythonanywhere.com/media/image/img_tmp_tag1740339581455_1.jpg'/>
                <body>
                </html>
    """

                send_mail(subject=subject, recipient_list=recipient, message='', from_email=sender,html_message=html_content)
                data = {'message': f'a password recovery code was sent to {email}',
                        'email': email
                        }
                return Response(data)
            except Exception:
                return Response({'message': 'error sending email'})
        else:
            return Response({'message': 'email does not exist'})
            

class ResendOtpView(APIView):

    def get(self, request, email):
            User = get_user_model()
            user = User.objects.filter(email=email).first()
            try:
                otp = secrets.token_hex(3)
                otp_token = OtpTokenGenerator.objects.create(user=user, otp_token=make_password(otp), otp_expires_at=timezone.now() + timezone.timedelta(minutes=30))
                otp_token.save()

                subject = 'Forgotten Password'
                recipient = [email]
                sender = settings.EMAIL_HOST_USER
                html_content = f""" 
                <html>
                <head>

                </head>
                <body>
                <h1> Password Reset Email </h1>
                <p> Dear {user.first_name}, </p>
                <p> we received a request to reset your password for your safemall account. </p>
                <p> To verify your identity, we've generated a one-time password (OTP) code:
                <h1> {otp} </h1>
                <p> Please enter this code in the password recovery page to proceed with resetting your password. </p>
                <p> This code is valid for 30 minutes. If you have any issues resetting your password, please contact our support team at safemall202@gmail.com.
                <p> For your security, we recommend choosing a strong and unique password. </p>
                <p>Best regards, </p>
                <p> Safemall </p>
                <img src='https://safemall.pythonanywhere.com/media/image/img_tmp_tag1740339581455_1.jpg'/>
                <body>
                </html>
    """

                send_mail(subject=subject, recipient_list=recipient, message='', from_email=sender,html_message=html_content)
                data = {'message': f'a password recovery code was sent to {email}',
                        'email': email
                        }
                return Response(data)
            except Exception:
                return Response({'message': 'error sending email'})


class OtpVerificationView(APIView):

    def get(self, request, email):
        otp = request.data['otp_token']
        User = get_user_model()
        user = get_object_or_404(User, email=email)
        otp_token = OtpTokenGenerator.objects.filter(user=user).last()
        if check_password(otp, otp_token.otp_token) and otp_token.otp_expires_at > timezone.now():
            data = {'message': 'otp verified',
                    'email': user.email,
                    }
            return Response(data)
        elif check_password(otp, otp_token.otp_token) and otp_token.otp_expires_at < timezone.now():
            return Response({'message': 'expired otp token'})
        else:
            return Response({'message': 'invalid otp token'})
        

    def post(self, request, email):
        User = get_user_model()
        password = request.data['password']
        user = get_object_or_404(User, email=email)
        user.password = password
        user.set_password(password)
        user.save()
        return Response({'message': 'password resetted successfully'})



class OtpCodeVerificationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        otp = request.data['otp_token']
        user = request.user
        otp_token = OtpTokenGenerator.objects.filter(user=user).last()
        if check_password(otp, otp_token.otp_token) and otp_token.otp_expires_at > timezone.now():
            data = { 
                'message': 'otp verified'}
            return Response(data)
        elif check_password(otp, otp_token.otp_token) and otp_token.otp_expires_at < timezone.now():
            data = {
                'message': 'expired otp token'}
            return Response(data)
        else:
            data = {
                'message': 'invalid otp token'}
            return Response(data)
        

    def post(self, request):
        password = request.data['password']
        user = request.user
        user.password = password
        user.set_password(password)
        user.save()
        data = {
            'message': 'password resetted successfully'}
        return Response(data)
    


class ResetTransactionPinView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            otp = secrets.token_hex(3)
            otp_token = TransactionOtpTokenGenerator.objects.create(user=user, otp_token=make_password(otp), otp_expires_at=timezone.now() + timezone.timedelta(minutes=15))
            otp_token.save()        

            subject = 'Transaction PIN Reset Request'
            recipient = [user.email]
            sender = settings.EMAIL_HOST_USER

            html_body = f""" 
                    <html>
                    <head>

                    </head>
                    <body>
                    <h1> Transaction PIN Reset Email </h1>
                    <p> Dear {user.first_name}, </p>
                    <p> we received a request to reset your transaction PIN for your safemall account. </p>
                    <p> To verify your identity, we've generated a one-time password (OTP) code:
                    <h1> {otp} </h1>
                    <p> Please enter this code in the transaction PIN reset page to proceed with resetting your PIN. </p>
                    <p> This code is valid for 15 minutes. If you have any issues resetting your PIN, please contact our support team at safemall202@gmail.com.
                    <p> For your security, we recommend choosing a unique and confidential PIN. </p>
                    <p>Best regards, </p>
                    <p> Safemall </p>
                    <img src='https://safemall.pythonanywhere.com/media/image/img_tmp_tag1740339581455_1.jpg'/>
                    <body>
                    </html>
        """

            send_mail(subject=subject, recipient_list=recipient, message='', from_email=sender, html_message=html_body, fail_silently=False)
            data = { 
                'message': f'an otp code was sent to {user.email}'}
            return Response(data)
        except Exception:
            data = {
                'message': 'error sending email'}
            return Response(data)
        


class VerifyTransactionOtp(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        otp = request.data['otp_token']
        otp_token = TransactionOtpTokenGenerator.objects.filter(user=user).last()
        if check_password(otp, otp_token.otp_token) and otp_token.otp_expires_at > timezone.now():
            data = {
                'message': 'otp verified'}
            return Response(data)
        elif check_password(otp, otp_token.otp_token) and otp_token.otp_expires_at < timezone.now():
            data = {
                'message': 'expired otp token'}
            return Response(data)
        else:
            data = {
                'message': 'invalid otp token'}
            return Response(data)
        

    def post(self, request):
        pin = request.data['pin']
        user = request.user
        user.transaction_pin = make_password(pin)
        user.save()
        data = {
            'message': 'pin resetted successfully'}
        return Response(data)
    


class CheckPasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        password = request.data['password']
        if check_password(password, user.password):
            data = { 
                'message': 'valid password'}
            return Response(data)
        else:
            data = {
                'message': 'invalid password'}
            return Response(data)


class ResetEmailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data['email']
        User = get_user_model()
        user = request.user
        if email:
            if not User.objects.filter(email=email).exists():
                user.email = email
                user.email_verified = False
                user.save()
                vendor = VendorProfile.objects.filter(user=user).first()
                if vendor:
                    vendor.vendor_email = email
                    vendor.save()
                data = { 
                    'message': 'email changed successfully'}
                return Response(data)
            else:
                data = { 
                    'message': 'email already exists'}
                return Response(data)
        else:
            data = {
                'message': 'input an email address'}
            return Response(data)
        

class EmailVerificationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user 
        try:
            otp = secrets.token_hex(3)
            new_otp_token = EmailOtpTokenGenerator.objects.create(user=user, otp_token=make_password(otp), otp_expires_at = timezone.now() + timezone.timedelta(minutes=30))
            new_otp_token.save()
            sender = settings.EMAIL_HOST_USER
            subject = 'Verify Your Email Address'
            recipient = [user.email]
            html_body = f""" 
                        <html>
                        <head>

                        </head>
                        <body>
                        <h1> Email verification </h1>
                        <p> Dear {user.first_name}, </p>
                        <p> Thank you for creating an account with Safemall. </p>
                        <p> To ensure that we can communicate with you securely, we need to verify your email address. </p>
                        <p> Please enter the following verification code: </p>
                        <h1> {otp} </h1>
                        <p> This verification code is valid for 30 minutes. If you have any issues verifying your email address, please contact our support team at safemall202@gmail.com.
                        <p> Thank you for your cooperation. </p>
                        <p>Best regards, </p>
                        <p> Safemall </p>
                        <img src='https://safemall.pythonanywhere.com/media/image/img_tmp_tag1740339581455_1.jpg'/>
                        <body>
                        </html>
            """
            send_mail(from_email=sender, subject=subject, recipient_list=recipient, message='', html_message=html_body, fail_silently=False)
            data = { 
                'message': f'an email verification code was sent to {user.email}'}
            return Response(data)
        except Exception:
            data = {
                'message': 'error sending email'}
            return Response(data)
        

class EmailOtpVerificationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        otp_code = request.data['otp_code']
        user = request.user
        otp_token = EmailOtpTokenGenerator.objects.filter(user=user).last()
        if check_password(otp_code, otp_token.otp_token) and otp_token.otp_expires_at > timezone.now():
            user.email_verified = True
            user.save()
            data = { 
                'message': 'email verified'}
            return Response(data)
        elif check_password(otp_code, otp_token.otp_token) and otp_token.otp_expires_at < timezone.now():
            data = { 
                'message': 'expired otp token'}
            return Response(data)
        else:
            data = { 
                'message': 'invalid otp token'}
            return Response(data)
        


class DepositMoneyView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = int(request.data['amount'])
            email = request.user.email

            paystack_response = Paystack.initialize_transaction(email, amount)

            if paystack_response.get('status'):

                data = {
                    
                    'message': 'transaction initialized',
                    'data': paystack_response['data']
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                data = {
                    
                    'data': paystack_response
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            data = {
                
                'message': 'Deposit error'}
            return Response(data)
        

class VerifyDepositView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            reference = request.data['reference']
            paystack_response = Paystack.verify_transaction(reference)

            if paystack_response.get('status'):
                data = paystack_response.get('data')
                response_status = data['status']
                amount = Decimal(data['amount'])/100 #convert to naira
                email = data['customer']['email']

                if response_status == 'success':
                    wallet = Wallet.objects.get(user=request.user)
                    wallet.funds += amount
                    wallet.save()

                    transaction_history = TransactionHistory.objects.create(user=request.user, transaction_id=str(uuid.uuid4().int)[:20], transaction='Credit', transaction_type='Deposit', transaction_amount=amount,
                                                                                    sender='', recipient='Wallet')
                    transaction_history.save()

                    

                    data = {
                        
                        'message': 'deposit successful',
                        'new_balance': wallet.funds
                    }
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    data = { 
                        'error': 'transaction failed'}
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            data = { 
                'message': 'Deposit error, try refreshing'}
            return Response(data)
        


class FindRecipientView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            account_number = request.data['account_number']
            bank_code = request.data['bank_code']

            paystack_response = Paystack.find_recipient(account_number, bank_code)

            if paystack_response.status_code == 200 and paystack_response.json().get('status'):
                account_name = paystack_response.json()['data']['account_name']
                return Response({'account_name': account_name})
            else:
                data = {
                    
                    'message': 'error resolving account',
                    'data': paystack_response.json()
                }
                return Response(data)
        except Exception as e:
            data = { 
                'message': 'error getting account details'}
            return Response(data)


#
class WithdrawFundsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            recipient_name = request.data['recipient_name']
            recipient_account_number = request.data['recipient_account_number']
            recipient_bank_code = request.data['recipient_bank_code']
            recipient_amount = request.data['recipient_amount']

            paystack_response = Paystack.create_transfer_recipient(recipient_account_number, recipient_bank_code, recipient_name)
            recipient_data = paystack_response.json()

            if paystack_response.status_code not in [200, 201] or not recipient_data.get('status'):
                data = {'message': 'error creating tranfer recipient',
                        'error': recipient_data
                        }
                return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                recipient_code = recipient_data['data']['recipient_code']

                transfer_response = Paystack.initiate_transfer(recipient_amount, recipient_code)
                transfer_data = transfer_response.json()

                if transfer_response.status_code not in [200, 201] or not transfer_data.get('status'):
                    data = {
                        'message': 'error initiating transfer',
                        'error': transfer_data
                            }
                    return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    transfer_code = transfer_data['data']['transfer_code']
                    #wallet = Wallet.objects.get(user=request.user)
                    #wallet.funds -= Decimal
                    #wallet.save()
                    data = {
                        'message': 'transfer initiated successfully',
                        'transfer_code': transfer_code
                    }
                    return Response(data)
        except Exception:
            return Response({'message': 'an error occured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GeneralSearchView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request):
        search_query = request.GET.get('search')
        product_school = request.data['school']
        if search_query is not None:

            if product_school:
                product = Product.objects.filter(product_name__icontains=search_query).order_by('-uploaded_at') | Product.objects.filter(vendor_name__icontains=search_query).order_by('-uploaded_at')  and Product.objects.filter(school=product_school).order_by('-uploaded_at') 
                serializer = ProductSerializer(product, many=True)
                return Response(serializer.data)
            else:  
                product = Product.objects.filter(product_name__icontains=search_query).order_by('-uploaded_at')  | Product.objects.filter(vendor_name__icontains=search_query).order_by('-uploaded_at')  
                serializer = ProductSerializer(product, many=True)
                return Response(serializer.data)
        else:
            return Response({'message': []})


class SchoolFilterView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        school = request.data['product_school']
        category = request.data['product_category']

        if school and not category:
            product = Product.objects.filter(school=school).order_by('-uploaded_at') 
            serializer = ProductSerializer(product, many=True)
            return Response(serializer.data)
        elif category and not school:
            product = Product.objects.filter(product_category=category).order_by('-uploaded_at') 
            serializer = ProductSerializer(product, many=True)
            return Response(serializer.data)
        elif category and school:
            product = Product.objects.filter(product_category=category).order_by('-uploaded_at') and Product.objects.filter(school=school).order_by('-uploaded_at') 
            serializer = ProductSerializer(product, many=True)
            return Response(serializer.data)
        else:
            return Response({'message': 'please provide an input'})

