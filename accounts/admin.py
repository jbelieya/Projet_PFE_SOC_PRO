from django.contrib import admin

from accounts.models import User
from incidents.models import Incident
# Register your models here.
admin.site.register(User)

class IncidentAdmin(admin.ModelAdmin):
    list_display = ('incident_id_formatted', 'titre', 'user_name')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user_name':
            kwargs['queryset'] = User.objects.filter(role__in=['ANALYSTE_N1', 'ANALYSTE_N2'])
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'user_name':
            field.label_from_instance = lambda obj: f"{obj.username} ({obj.get_role_display()})"
        return field
