
# urls.py
from django.urls import path
from .views import SignUpView

urlpatterns = [
    path('api/v1/auth/signup/', SignUpView.as_view(), name='signup'),
]

# urlpatterns = [
#     path(
#         'auth/signup/',
#         TemplateView.as_view(template_name='redoc.html'),
#         name='redoc'
#     ),
# ]