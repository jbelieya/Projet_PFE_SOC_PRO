from rest_framework import serializers
from .models import HistoriqueAudit

class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = HistoriqueAudit
        fields = ['id', 'username', 'action_type', 'description_change', 'date_change', 'id_incident']