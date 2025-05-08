from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404

from django.core.files.base import ContentFile
import re
import json
import base64

class ChatConsumer(WebsocketConsumer):

    @database_sync_to_async
    def get_chatroom(self, group_name):
        from .models import GroupName
        return get_object_or_404(GroupName, group_name=group_name)

    # @database_sync_to_async
    # def create_message(self, user, content, chatroom, group_name, user_chat_id):
    #     return UserMessage.objects.create(
    #         user=user,
    #         message_type='text',
    #         group=chatroom,
    #         group_name=group_name,
    #         user_chat_id=user_chat_id,
    #         message=content
    #     )

    def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs']['chatroom_name']
        
        self.user = self.scope['user']
        async_to_sync(self.channel_layer.group_add)(
                 self.room_group_name,
                 self.channel_name
             )
        self.accept()



    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


    def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        from .models import UserMessage
        self.chatroom = async_to_sync(self.get_chatroom)(self.room_group_name)

        if message_type == 'text':
            content = data.get('content')

            UserMessage.objects.create(
                user=self.user,
                message_type = 'text',
                group=self.chatroom,
                group_name = self.room_group_name,
                user_chat_id = self.user.user_chat_id,
                message=content
            )

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': content
                }
            )
            from firebase_admin import messaging, exceptions
            from .models import VendorProfile
            
            if self.user == self.chatroom.user_1:
                
                recipient_user = self.chatroom.user_2
                user_token = recipient_user.fcm_token
                
                if VendorProfile.objects.filter(user=recipient_user).exists():
                    vendor = VendorProfile.objects.get(user=recipient_user)
                    name = vendor.business_name
                else:
                    name = f'{recipient_user.first_name} {recipient_user.last_name}'
                
                image_url = self.get_image_url(recipient_user.profile_image)
                print(image_url)
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=name,
                        body=content,
                        image= image_url
                    ),
                    android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                    image=image_url
                    )
                        ),
                    token=user_token,

                    )
                try:
                    messaging.send(message)
                except exceptions.FirebaseError as e:
                    if 'NotRegistered' in str(e) or 'InvalidRegistration' in str(e):
                        recipient_user.fcm_token = ''
                        recipient_user.save()

            elif self.user == self.chatroom.user_2:
                
                recipient_user = self.chatroom.user_1
                user_token = recipient_user.fcm_token
                
                if VendorProfile.objects.filter(user=recipient_user).exists():
                    vendor = VendorProfile.objects.get(user=recipient_user)
                    name = vendor.business_name
                else:
                    name = f'{recipient_user.first_name} {recipient_user.last_name}'
                
                image_url = self.get_image_url(recipient_user.profile_image)
                print(image_url)
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=name,
                        body=content,
                        image= image_url
                    ),
                    android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                    image=image_url
                    )
                        ),
                    token=user_token,

                    )
                try:
                    messaging.send(message)
                except exceptions.FirebaseError as e:
                    if 'NotRegistered' in str(e) or 'InvalidRegistration' in str(e):
                        recipient_user.fcm_token = ''
                        recipient_user.save()

        elif message_type == 'file':
            filename = data.get('filename')
            file_content_base64 = data.get('content')
            match = re.match(r'data:(image/\w+);base64,(.+)', file_content_base64)
            if match:
                file_content_base64 = match.group(2)
            file_content = base64.b64decode(file_content_base64)
            file = ContentFile(file_content, name=filename)

            user_message = UserMessage.objects.create(
                message_type='file',
                user=self.user,
                group=self.chatroom,
                group_name = self.chatroom.group_name,
                user_chat_id = self.user.user_chat_id,
                file=file,
            )

            file_url = user_message.file.url

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'type': 'file',
                        'url': file_url,
                        'filename': filename,
                    }
                }
            )


            from firebase_admin import messaging, exceptions
            from .models import VendorProfile
            
            if self.user == self.chatroom.user_1:
                
                recipient_user = self.chatroom.user_2
                user_token = recipient_user.fcm_token
                
                if VendorProfile.objects.filter(user=recipient_user).exists():
                    vendor = VendorProfile.objects.get(user=recipient_user)
                    name = vendor.business_name
                else:
                    name = f'{recipient_user.first_name} {recipient_user.last_name}'
                
                image_url = self.get_image_url(recipient_user.profile_image)
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=name,
                        body='photo 📷',
                        image= image_url
                    ),
                    android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                    image=image_url
                    )
                        ),
                    token=user_token,

                    )
                try:
                    messaging.send(message)
                except exceptions.FirebaseError as e:
                    if 'NotRegistered' in str(e) or 'InvalidRegistration' in str(e):
                        recipient_user.fcm_token = ''
                        recipient_user.save()

            elif self.user == self.chatroom.user_2:
                
                recipient_user = self.chatroom.user_1
                user_token = recipient_user.fcm_token
                
                if VendorProfile.objects.filter(user=recipient_user).exists():
                    vendor = VendorProfile.objects.get(user=recipient_user)
                    name = vendor.business_name
                else:
                    name = f'{recipient_user.first_name} {recipient_user.last_name}'
                
                image_url = self.get_image_url(recipient_user.profile_image)

                message = messaging.Message(
                    notification=messaging.Notification(
                        title=name,
                        body='photo 📷',
                        image= image_url
                    ),
                    android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                    image=image_url
                    )
                        ),
                    token=user_token,

                    )
                try:
                    messaging.send(message)
                except exceptions.FirebaseError as e:
                    if 'NotRegistered' in str(e) or 'InvalidRegistration' in str(e):
                        recipient_user.fcm_token = ''
                        recipient_user.save()

        
        elif message_type == 'voicemessage':
            filename = data.get('filename')
            file_content_base64 = data.get('content')

            match = re.match(r'data:(audio/\w+);base64,(.+)', file_content_base64)
            if match:
                file_content_base64 = match.group(2)

            file_content = base64.b64decode(file_content_base64)
            file = ContentFile(file_content, name=filename)

            user_message = UserMessage.objects.create(
                message_type='voice',
                user=self.user,
                group=self.chatroom,
                group_name=self.chatroom.group_name,
                user_chat_id=self.user.user_chat_id,
                file=file,
            )

            file_url = user_message.file.url

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'type': 'voice',
                        'url': file_url,
                        'filename': filename,
                    }
                }
            )

            from firebase_admin import messaging, exceptions
            from .models import VendorProfile
            
            if self.user == self.chatroom.user_1:
                
                recipient_user = self.chatroom.user_2
                user_token = recipient_user.fcm_token
                
                if VendorProfile.objects.filter(user=recipient_user).exists():
                    vendor = VendorProfile.objects.get(user=recipient_user)
                    name = vendor.business_name
                else:
                    name = f'{recipient_user.first_name} {recipient_user.last_name}'
                
                image_url = self.get_image_url(recipient_user.profile_image)
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=name,
                        body='voice 🔊',
                        image= image_url
                    ),
                    android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                    image=image_url
                    )
                        ),
                    token=user_token,

                    )
                try:
                    messaging.send(message)
                except exceptions.FirebaseError as e:
                    if 'NotRegistered' in str(e) or 'InvalidRegistration' in str(e):
                        recipient_user.fcm_token = ''
                        recipient_user.save()

            elif self.user == self.chatroom.user_2:
                
                recipient_user = self.chatroom.user_1
                user_token = recipient_user.fcm_token
                
                if VendorProfile.objects.filter(user=recipient_user).exists():
                    vendor = VendorProfile.objects.get(user=recipient_user)
                    name = vendor.business_name
                else:
                    name = f'{recipient_user.first_name} {recipient_user.last_name}'
                
                
                image_url = self.get_image_url(recipient_user.profile_image)
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=name,
                        body='voice 🔊',
                        image= image_url
                    ),
                    android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                    image=image_url
                    )
                        ),
                    token=user_token,

                    )
                try:
                    messaging.send(message)
                except exceptions.FirebaseError as e:
                    if 'NotRegistered' in str(e) or 'InvalidRegistration' in str(e):
                        recipient_user.fcm_token = ''
                        recipient_user.save()

        elif message_type == 'typing':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': 'typing...'
                }
            )



        
    def chat_message(self, event):
        content = event['message']

        self.send(text_data=json.dumps({
            'message': content
        }))



    def get_image_url(self, file_field):
        scheme = 'https'
        host = self.scope.get('headers', [])
        host_value = next(
            (value.decode() for key, value in host if key == b'host'),
            'localhost:8000'
        )
        return f"{scheme}://{host_value}{file_field.url}"
