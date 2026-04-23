from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import User  # adjust if your app name differs
from .serializers import (
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserApprovalSerializer,
)


class IsAdminOrManager(IsAuthenticated):
    """Allow access only to admin or manager roles."""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ('admin', 'manager') or request.user.is_superuser


# ─── List & Create ────────────────────────────────────────────────────────────

class UserListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/admin/users/        → list all users (with filters & search)
    POST /api/admin/users/        → create a new user
    """
    permission_classes = [IsAdminOrManager]
    queryset = User.objects.all().order_by('-date_joined')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_approved', 'is_verified', 'is_active', 'is_online']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telephone']
    ordering_fields = ['date_joined', 'username', 'role']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer


# ─── Retrieve, Update, Delete ─────────────────────────────────────────────────

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/admin/users/<id>/   → retrieve user
    PUT    /api/admin/users/<id>/   → full update
    PATCH  /api/admin/users/<id>/   → partial update
    DELETE /api/admin/users/<id>/   → delete user
    """
    permission_classes = [IsAdminOrManager]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserListSerializer
        return UserUpdateSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response(
                {'detail': 'You cannot delete your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.delete()
        return Response({'detail': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


# ─── Approve / Reject ─────────────────────────────────────────────────────────

class UserApproveView(APIView):
    """
    PATCH /api/admin/users/<id>/approve/   → approve user
    PATCH /api/admin/users/<id>/reject/    → reject (unapprove) user
    """
    permission_classes = [IsAdminOrManager]

    def patch(self, request, pk, action):
        user = get_object_or_404(User, pk=pk)
        if action == 'approve':
            user.is_approved = True
            msg = f"User '{user.username}' approved successfully."
        elif action == 'reject':
            user.is_approved = False
            msg = f"User '{user.username}' rejected."
        else:
            return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
        user.save()
        return Response({'detail': msg, 'is_approved': user.is_approved})


# ─── Stats ────────────────────────────────────────────────────────────────────

class UserStatsView(APIView):
    """
    GET /api/admin/users/stats/  → quick dashboard stats
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request):
        qs = User.objects.all()
        stats = {
            'total': qs.count(),
            'approved': qs.filter(is_approved=True).count(),
            'pending': qs.filter(is_approved=False).count(),
            'online': qs.filter(is_online=True).count(),
            'by_role': {
                role: qs.filter(role=role).count()
                for role, _ in User.ROLE_CHOICES
            },
        }
        return Response(stats)


# ─── Bulk Actions ─────────────────────────────────────────────────────────────

class UserBulkActionView(APIView):
    """
    POST /api/admin/users/bulk/
    Body: { "ids": [1,2,3], "action": "approve"|"reject"|"activate"|"deactivate" }
    """
    permission_classes = [IsAdminOrManager]

    def post(self, request):
        ids = request.data.get('ids', [])
        action = request.data.get('action')

        if not ids or not action:
            return Response({'detail': 'ids and action are required.'}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(pk__in=ids)
        count = users.count()

        action_map = {
            'approve':     lambda qs: qs.update(is_approved=True),
            'reject':      lambda qs: qs.update(is_approved=False),
            'activate':    lambda qs: qs.update(is_active=True),
            'deactivate':  lambda qs: qs.update(is_active=False),
        }

        if action not in action_map:
            return Response({'detail': f'Unknown action: {action}'}, status=status.HTTP_400_BAD_REQUEST)

        action_map[action](users)
        return Response({'detail': f'{action} applied to {count} user(s).'})