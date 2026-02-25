from django.db import models
from django.conf import settings
from django.utils import timezone
from accounts.models import User
# Create your models here.

class Incident(models.Model):
    # choices for various fields
    INSITER_TYPO_CHOICES = [('Mineur', 'Mineur'), ('Majeur', 'Majeur')]
    SEVERITY_CHOICES = [('High', 'High'), ('Low', 'Low'), ('Medium', 'Medium'), ('Critical', 'Critical')]
    CATEGORY_CHOICES = [
        ('Application', 'Application'),
        ('Web', 'Web'),
        ('Email', 'Email'),
        ('Authentification', 'Authentification')
    ]
    PLANT_CHOICES = [('Site', 'Site'), ('COFTN', 'COFTN'), ('COFFR', 'COFFR')]
    HOST_STATE_CHOICES = [('Blocked', 'Blocked'), ('Not Blocked', 'Not Blocked')]
    STATUS_CHOICES = [('Open', 'Open'), ('In Progress', 'In Progress'), ('Closed', 'Closed')]
    YES_NO_CHOICES = [('Yes', 'Yes'), ('No', 'No')]

    #Fields based
    id_incident = models.AutoField(primary_key=True)  # Auto-increment
    incident_id_formatted = models.CharField(max_length=100, help_text="Format: Date_Now + Nombre",null=True, blank=True)  # Champ pour stocker l'ID formaté
    titre = models.CharField(max_length=255, null=True, blank=True)
    date_detection = models.DateTimeField(default=timezone.now)
    insiter_typo = models.CharField(max_length=10, choices=INSITER_TYPO_CHOICES,null=True, blank=True)
    severity_level = models.CharField(max_length=10, choices=SEVERITY_CHOICES,null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES,null=True, blank=True)
    plant_name = models.CharField(max_length=20, choices=PLANT_CHOICES,null=True, blank=True)
    
    raised_by = models.CharField(max_length=100, null=True, blank=True)
    host_name = models.CharField(max_length=100, null=True, blank=True)
    user_name_pc = models.CharField(max_length=100, null=True, blank=True)
    host_state = models.CharField(max_length=15, choices=HOST_STATE_CHOICES,null=True, blank=True)
    
    description_investigation = models.TextField(null=True, blank=True)
    remediation_destination = models.CharField(max_length=255, null=True, blank=True)
    first_event = models.DateTimeField(null=True, blank=True)
    
    ticket_relise = models.CharField(max_length=3, choices=YES_NO_CHOICES,null=True, blank=True)
    escalation = models.CharField(max_length=3, choices=YES_NO_CHOICES,null=True, blank=True)
    incident_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open',null=True, blank=True)
    false_position = models.CharField(max_length=3, choices=YES_NO_CHOICES,null=True, blank=True)
    
    impact_on_cofi_cob = models.TextField(null=True, blank=True)
    help_desk_ticket_nb = models.CharField(max_length=50, null=True, blank=True)
    date_target = models.DateTimeField(default=timezone.now)
    time_of_closed_incident = models.DateTimeField(null=True, blank=True)
    acknowledge_time = models.DateTimeField(null=True, blank=True)
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur associé",null=True, blank=True)  # Relie l'incident à un utilisateur (analyste)

    def __str__(self):
        return f"{self.incident_id_formatted} - {self.titre}"

    # Example of the generateIncidentID logic
    def save(self, *args, **kwargs):
        if not self.incident_id_formatted:
            # Logic to format Date_Now + Number
            date_str = timezone.now().strftime('%Y%m%d')
            count = Incident.objects.filter(date_detection__date=timezone.now().date()).count() + 1
            self.incident_id_formatted = f"{date_str}_{count}"
        super(Incident, self).save(*args, **kwargs)


