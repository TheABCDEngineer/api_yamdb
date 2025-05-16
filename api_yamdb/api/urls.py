from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import ApiCategory, ApiGenre, TitleViewSet, SignUpView, TokenObtainView, UserViewSet

router_v1 = DefaultRouter()
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('genres', ApiGenre, basename='genres')
router_v1.register('categories', ApiCategory, basename='categories')
router_v1.register(
  prefix='users',
  viewset=UserViewSet, 
  basename='user'
)
router_v1.register(
    prefix='titles',
    viewset=views.TitleViewSet,
    basename='titles'
)
router_v1.register(
    prefix=r'titles/(?P<title_id>\d+)/reviews',
    viewset=views.ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    prefix=r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    viewset=views.CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path(
        'v1/auth/token/',
        TokenObtainView.as_view(),
        name='token_obtain_pair'
    ),
    path('v1/', include(router_v1.urls)),
]
