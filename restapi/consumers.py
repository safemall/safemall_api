from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from .models import GroupName, UserMessage
from django.core.files.base import ContentFile
import re
import json
import base64

class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs']['chatroom_name']
        
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.chatroom = get_object_or_404(GroupName, group_name=self.room_group_name)
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

        if message_type == 'text':
            content = data.get('content')

            UserMessage.objects.create(
                user=self.user,
                message_type = 'text',
                group=self.chatroom,
                group_name = self.chatroom.group_name,
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
