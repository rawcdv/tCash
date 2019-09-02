from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()

class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} -> {self.receiver.username}"

    def messagesWith(user, counterparty):
        return Message.objects.filter(
            models.Q(author=user, receiver=counterparty)
            | 
            models.Q(receiver=user, author=counterparty)
        ).order_by("timestamp")

    def get_headlines(user):
        # TODO: optimize using distinct(columns) once we move from sqlite
        allMessages = Message.objects.filter(
            models.Q(author=user) | models.Q(receiver=user))

        lastTimestamp = {}
        for currMsg in allMessages:
            content = currMsg.content
            timestamp = currMsg.timestamp
            # assign counterparty as the one who isn't the user
            counterparty = currMsg.receiver.username if currMsg.author == user else currMsg.author.username

            if counterparty in lastTimestamp:
                currLatest = lastTimestamp[counterparty]["timestamp"]
                if currLatest > currMsg.timestamp:
                    continue

            lastTimestamp[counterparty] = {
                "content": content,
                "timestamp": timestamp
            }

        # parse latest timestamps into list
        latestMessages = []
        for k,v in lastTimestamp.items():
            latestMessages.append({
                "counterparty": k,
                "content": v["content"],
                "timestamp": v["timestamp"]
            })

        # sort list
        latestMessages = sorted(latestMessages, key=lambda k: k['timestamp'], reverse=True)
        return latestMessages
