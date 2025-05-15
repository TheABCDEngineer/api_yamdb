# models.py
import random

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
import string

def generate_activation_code():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))


class ActivationCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    code = models.CharField(max_length=6, default=generate_activation_code)



from django.http import Http404

def register_user(request):
    code = ActivationCode.objects.create(user=request.data['username'])
    send_mail(
        'Activate Your Account',
        'Here is the activation code: %s' % code,
        'from@example.com',
        [request.data['email']]
    )

def check_activation_code(request, code):
    try:
        ActivationCode.objects.get(code=code)
    except ActivationCode.DoesNotExist:
        raise Http404
