from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


router_v1 = DefaultRouter()
router_v1.register(
    prefix='genres',
    viewset=views.GenreViewSet,
    basename='genres'
)
router_v1.register(
    prefix='categories',
    viewset=views.CategoryViewSet,
    basename='categories'
)
router_v1.register(
    prefix='users',
    viewset=views.UserViewSet,
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
    path(
        route='v1/auth/signup/',
        view=views.SignUpView.as_view(),
        name='signup'
    ),
    path(
        route='v1/auth/token/',
        view=views.TokenObtainView.as_view(),
        name='token_obtain_pair'
    ),
    path('v1/', include(router_v1.urls)),
]
