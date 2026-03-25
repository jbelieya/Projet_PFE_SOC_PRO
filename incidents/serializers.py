from rest_framework import serializers
from .models import Incident

class IncidentSerializer(serializers.ModelSerializer):
    user_name_display = serializers.ReadOnlyField(source='user_name.username')
    user_id = serializers.ReadOnlyField(source='user_name.id')
    class Meta:
        model = Incident
        fields = '__all__'

    def get_mttd(self, obj):
        # obj houwa l-incident li 9a3din n-serialize-iw fih
        if obj.first_event and obj.date_detection:
            diff = obj.date_detection - obj.first_event
            return round(diff.total_seconds() / 60, 2)
        return 0 # Kén m-famech data, rajja3 0

    