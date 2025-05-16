from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ApiCategory, ApiGenre, TitleViewSet

api_v1_router = DefaultRouter()
api_v1_router.register('titles', TitleViewSet, basename='titles')
api_v1_router.register('genres', ApiGenre, basename='genres')
api_v1_router.register('categories', ApiCategory, basename='categories')

urlpatterns = [
    path('v1/', include(api_v1_router.urls)),
]
