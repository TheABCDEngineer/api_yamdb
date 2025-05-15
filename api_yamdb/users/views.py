import string
from random import choice


from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
#from .serializers import TokenObtainSerializer

import string
from random import choice


def generate_confirmation_code():
    return ''.join(choice(string.ascii_uppercase + string.digits) for x in range(6))

class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            self.send_confirmation_code(user.email, user.confirmation_code)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_confirmation_code(self, email, code):
        send_mail(
            subject='Ваш код подтверждения',
            message=f'Ваш код: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

# class TokenObtainView(APIView):
#     permission_classes = []  
#     authentication_classes = []

#     def post(self, request):
#         serializer = TokenObtainSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response(serializer.validated_data, status=status.HTTP_200_OK)



# class SignUpView(APIView):
#     """View-класс для эндпоинта регистрации."""
#     def post(self, request):
#         users = 