from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views


router_v1 = SimpleRouter()
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
    path('v1/', include(router_v1.urls)),
]
