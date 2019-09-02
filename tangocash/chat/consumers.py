from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import Message

User = get_user_model()

class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        counterparty = User.objects.filter(username=data["counterparty"]).get()
        self.user = self.scope["user"]
        messages = Message.messagesWith(self.user, counterparty)
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def fetch_headlines(self, data):
        self.user = self.scope["user"]
        messages = Message.get_headlines(self.user)
        content = {
            'command': 'headlines',
            'messages': self.headlines_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        # vulnerable to impersonation
        # author = data['from']
        author = self.scope["user"]
        receiver = data['to']
        author_user = User.objects.filter(username=author)[0]
        receiver_user = User.objects.filter(username=receiver)[0]
        message = Message.objects.create(
            author=author_user, 
            receiver=receiver_user,
            content=data['message'])
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'receiver': message.receiver.username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    def headlines_to_json(self, headlines):
        result = []
        for headline in headlines:
            result.append(self.headline_to_json(headline))
        return result

    def headline_to_json(self, headline):
        return {
            'counterparty': headline['counterparty'],
            'content': headline['content'],
            'timestamp': str(headline['timestamp'])
        }

    commands = {
        'fetch_messages': fetch_messages,
        'fetch_headlines': fetch_headlines,
        'new_message': new_message
    }

    def connect(self):
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_name = 'roomName'
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        print(text_data)
        self.commands[data['command']](self, data)
        

    def send_chat_message(self, message):    
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
