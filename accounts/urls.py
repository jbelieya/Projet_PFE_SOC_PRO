from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, MyLoginView, VerifyEmailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyLoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
]