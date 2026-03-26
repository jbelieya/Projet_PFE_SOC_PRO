from django.shortcuts import render
from rest_framework import viewsets, permissions

from audit.permissions import IsAdminRole
from .models import HistoriqueAudit
from .serializers import AuditLogSerializer
from rest_framework.permissions import AllowAny

# Create your views here.
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HistoriqueAudit.objects.all()
    serializer_class = AuditLogSerializer
    # Khalli ken l-Admin ychouf l-Historique
    permission_classes = [AllowAny]
