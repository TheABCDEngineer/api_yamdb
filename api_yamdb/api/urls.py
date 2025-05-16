from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SignUpView, TokenObtainView, UserViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path(
        'auth/token/',
        TokenObtainView.as_view(),
        name='token_obtain_pair'
    ),
    path('', include(router_v1.urls)),
]
