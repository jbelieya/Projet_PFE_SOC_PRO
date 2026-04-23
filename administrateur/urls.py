from django.urls import path
from .views import (
    UserListCreateView,
    UserDetailView,
    UserApproveView,
    UserStatsView,
    UserBulkActionView,
)

app_name = 'administrateur'

urlpatterns = [
    # Stats
    path('users/stats/', UserStatsView.as_view(), name='user-stats'),

    # Bulk actions
    path('users/bulk/', UserBulkActionView.as_view(), name='user-bulk'),

    # List & Create
    path('users/', UserListCreateView.as_view(), name='user-list-create'),

    # Retrieve / Update / Delete
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # Approve / Reject
    path('users/<int:pk>/<str:action>/', UserApproveView.as_view(), name='user-approve'),
]