from django.shortcuts import render
from rest_framework.response import Response
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.http import Http404
from .serializers import UserSerializer, BuyerSerializer, VendorSerializer, ProductSerializer, OrderDetailSerializer, ProductImageSerializer, ProductReviewSerializer
from .models import BuyerProfile, VendorProfile, Product, OrderDetail, ProductImage, ProductReview
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models.fields.files import ImageFieldFile
import secrets
import random
import uuid
from django.core.cache import cache
from django.db.models import Avg
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
                buyer_profile = BuyerProfile.objects.create(user=buyer, email=buyer.email, account_number='2' + str(uuid.uuid4().int)[:10-len('2')], first_name=buyer.first_name, last_name=buyer.last_name, phone_number=request.data['phone_number'])
                buyer_profile.save()
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
                vendor_profile = VendorProfile.objects.create(user=vendor, business_name='', profile_image='', account_number= '2' + str(uuid.uuid4().int)[:10-len('2')], business_address='', business_phone_number='')
                vendor_profile.save()
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
        vendor.save()
        Vendorstore = VendorSerializer(vendor)
        return Response(Vendorstore.data, status=status.HTTP_201_CREATED)
    
    def put(self, request):
        user = get_object_or_404(VendorProfile, user=request.user)
        serializer = VendorSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProductUploadView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    
    def post(self, request):
        user = request.user
        vendor = get_object_or_404(VendorProfile, user=user)
        name = vendor.business_name
        identity = vendor.vendor_id
        vendor_image = vendor.profile_image
        serializer = ProductSerializer(data=request.data)
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
        


class ProductDetailsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get_object(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, product_id):
        product = self.get_object(product_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

       
    def post(self, request, product_id):
        quantity = int(request.data['quantity'])
        product = self.get_object(product_id)
        serializer = ProductSerializer(product)
        if int(quantity) < int(product.stock):
            cache.set(product_id, quantity, 3600)
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
    
    
    def delete(self, request, product_id):
        product = self.get_object(product_id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        

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
        quantity = cache.get(product_id)
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
        vendor = product.vendor_name
        vendor_id = product.vendor_identity
        quantity = cache.get(product_id)
        if quantity == None:
            return Response({'message': 'cache timeout'})
        total_sum = price* int(quantity)
        if serializer.is_valid():
            
                order = OrderDetail.objects.create(user = request.user, order_id = uuid.uuid4(), order_otp_token = secrets.token_hex(4), first_name=request.data['first_name'], last_name=request.data['last_name'], address=request.data['address'], phone_number=request.data['phone_number'], email_address=request.data['email_address'], 
                                                product_name=name, product_image = order_image.image, product_price=price, vendor_name=vendor, vendor_id =vendor_id, product_quantity=quantity, total_price = total_sum)      
                order.save()
                order_serializer = OrderDetailSerializer(order)                
                product.stock -= int(quantity)
                product.quantity_sold += int(quantity)
                product.save()
                
                return Response(order_serializer.data, status=status.HTTP_201_CREATED)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ClothesPageView(APIView):
    def get(self, request):
        clothpage = Product.objects.filter(product_category='clothes').order_by('-uploaded_at')
        clothserializer = ProductSerializer(clothpage, many=True)
        return Response(clothserializer.data)
    


class FoodPageView(APIView):
    def get(self, request):
        foodpage = Product.objects.filter(product_category='food').order_by('-uploaded_at')
        foodserializer = ProductSerializer(foodpage, many=True)
        return Response(foodserializer.data)
    

class FootwearsPageView(APIView):
    def get(self, request):
        footwearpage = Product.objects.filter(product_category='footwears').order_by('-uploaded_at')
        footwearserializer = ProductSerializer(footwearpage, many=True)
        return Response(footwearserializer.data)
    

class AccessoriesPageView(APIView):
    def get(self, request):
        accessoriespage = Product.objects.filter(product_category='accessories').order_by('-uploaded_at')
        accessoriesserializer = ProductSerializer(accessoriespage, many=True)
        return Response(accessoriesserializer.data)
    

class BeautyPageView(APIView):
    def get(self, request):
        beautypage = Product.objects.filter(product_category='beauty').order_by('-uploaded_at')
        beautyserializer = ProductSerializer(beautypage, many=True)
        return Response(beautyserializer.data)
    

class HouseholdPageView(APIView):
    def get(self, request):
        householdpage = Product.objects.filter(product_category='household').order_by('-uploaded_at')
        householdserializer = ProductSerializer(householdpage, many=True)
        return Response(householdserializer.data)
    

class NewArrivalsView(APIView):
    def get(self, request):
        total = Product.objects.count() - 3
        new_arrivals = Product.objects.all().order_by('-uploaded_at')[:20]
        serializer = ProductSerializer(new_arrivals, many=True)
        return Response(serializer.data)
    

class ExploreView(APIView):
    def get(self, request):
        max_id = VendorProfile.objects.values_list('id', flat=True)
        random_ids = random.sample(list(max_id), min(2, len(max_id)))
        random_data = VendorProfile.objects.filter(id__in=random_ids)
        vendor_serializer = VendorSerializer(random_data, many=True)
        return Response(vendor_serializer.data)
    

class FeaturedProductView(APIView):
    def get(self, request):
        max_id = Product.objects.values_list('id', flat=True)
        random_ids = random.sample(list(max_id), min(3, len(max_id)))
        random_data = Product.objects.filter(id__in=random_ids)
        product_serializer = ProductSerializer(random_data, many=True)
        return Response(product_serializer.data)


class VendorPageView(APIView):
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
          
    
class SearchProduct(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search_query = request.GET.get('search')
        if search_query is not None:
            product = Product.objects.filter(product_name__icontains=search_query) | Product.objects.filter(vendor_name__icontains=search_query)
            if not product:
                return Response({'message': f'No result found for {search_query}'}, status=status.HTTP_404_NOT_FOUND)
            print(product)
            serializer = ProductSerializer(product, many=True)
            return Response(serializer.data)
        else:
            return Response({'message': 'Please provide a search query'})



class ProductReviewView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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
            return Response({'message': 'No review(s) yet, be the first to drop a review'})
        
            

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
        vendor_order = OrderDetail.objects.filter(vendor_id=vendor_id).order_by('-created_at')
        if vendor_order:
            serializer = OrderDetailSerializer(vendor_order, many=True)
            return Response(serializer.data)
        else:
            return Response({'message': 'you have no order yet'})
        

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
            return Response({'message': 'you have not made any order yet'})
        

class InventoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        vendor = get_object_or_404(VendorProfile, user=user)
        vendor_id = vendor.vendor_id
        product = Product.objects.filter(vendor_identity=vendor_id).order_by('-uploaded_at')
        if product:
            serializer = ProductSerializer(product, many=True)
            return Response(serializer.data)
        else:
            return Response({'message': 'you have no inventory yet'})
