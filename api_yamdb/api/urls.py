from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ApiCategory, ApiGenre, CsvImportAPIView, TitlePost

api_v1_router = DefaultRouter()
api_v1_router.register('titles', TitlePost, basename='titles')
api_v1_router.register('genres', ApiGenre, basename='genres')
api_v1_router.register('categories', ApiCategory, basename='categories')

api_v1_urlpatterns = [
    path('', include(api_v1_router.urls)),
    path('import-csv/', CsvImportAPIView.as_view(), name='import-csv'),
]

urlpatterns = [
    path('v1/', include(api_v1_urlpatterns)),
]
