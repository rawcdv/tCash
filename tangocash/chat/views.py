# chat/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


User = get_user_model()

@login_required
def room(request):
    to_username = request.GET.get('to')
    if to_username is None:
        context = {
            'username': mark_safe(json.dumps(request.user.username)),
        }
    else:
        user = get_object_or_404(User, username=to_username)

        context = {
            'to_username': mark_safe(json.dumps(to_username)),
            'username': mark_safe(json.dumps(request.user.username)),
        }
        
    return render(request, 'chat/room.html', context=context)
