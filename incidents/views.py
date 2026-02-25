from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Incident
from .serializers import IncidentSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from rest_framework.decorators import action
from django.utils import timezone
# Create your views here.
class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [AllowAny]  
    # --- GET INCIDENT BY ID ---
    def retrieve(self, request, *args, **kwargs):
        """
        Action: Trajja3 les détails kemlin mta3 incident we7ed bel ID mte3ou.
        URL: GET /api/incidents/{id}/
        """
        instance = self.get_object() # Django y-lawaj 3al incident bel ID automatique
        serializer = self.get_serializer(instance)
        
        data = serializer.data
        
        # Faza zayda lel PFE: Calcul MTTA (wa9t el réponse mta3 l-analyste)
        if instance.acknowledge_time:
            diff = instance.acknowledge_time - instance.date_detection
            mtta_minutes = round(diff.total_seconds() / 60, 2)
            data['mtta_minutes'] = mtta_minutes
            
        return Response(data)
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        incident = self.get_object()
        if incident.incident_status != 'Open':
            return Response(
                {"error": "Impossible de clôturer un incident qui n'a pas été pris en charge (Acknowledge)."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if incident.user_name is not None and incident.user_name != request.user:
            return Response({'error': f'Déja pris en charge par {incident.user_name}.'}, status=status.HTTP_400_BAD_REQUEST)
        
        incident.user_name = request.user
        incident.acknowledge_time = timezone.now()
        incident.incident_status = 'In Progress'
        incident.save()
        
        return Response({
            "status": "In Progress",
            "analyst": request.user.username,
            "acknowledge_time": incident.acknowledge_time
        })
    # --- PHASE 3: Investigation & Traitement ---
    @action(detail=True, methods=['patch'])
    def investigate(self, request, pk=None):
        """
        L-analyste y3ammar el champs mta3 el ba7th mte3ou wa7da wa7da.
        """
        incident = self.get_object()
        if incident.incident_status != 'In Progress':
            return Response(
                {"error": "Le graphique d'investigation n'est disponible que pour les incidents 'In Progress'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        # Verification: Lezem el analyste elli 3mal acknowledge houwa elli ykammel
        if incident.user_name != request.user:
            return Response({'error': 'Vous n\'êtes pas l\'analyste assigné à cet incident.'}, status=403)

        # Liste mta3 el champs elli l-analyste ynajem ybaddelhom tawa
        allowed_fields = [
            'host_name', 'user_name_pc', 'host_state', 
            'severity_level', 'category', 'first_event', 
            'escalation', 'impact_on_cofi_cob', 'help_desk_ticket_nb',
            'description_investigation'
        ]

        # N-loopi 3al data elli jaya mel frontend
        for field in allowed_fields:
            if field in request.data:
                setattr(incident, field, request.data.get(field))

        incident.save()
        return Response({
            "message": "Investigation mise à jour avec succès",
            "incident_id": incident.incident_id_formatted
        }, status=status.HTTP_200_OK)


    # --- PHASE 4: Phase de Clôture (Final Step) ---
    @action(detail=True, methods=['post'])
    def close_incident(self, request, pk=None):
        """
        Tessaker el incident w t7ot el remediation wel wa9t niha'i.
        """
        incident = self.get_object()
        if incident.incident_status == 'Open':
            return Response(
                {"error": "Impossible de clôturer un incident qui n'a pas été pris en charge (Acknowledge)."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if incident.user_name != request.user:
            return Response({'error': 'Seul l\'analyste responsable peut clôturer cet incident.'}, status=403)

        # 1. Mise à jour des champs de clôture
        incident.remediation_destination = request.data.get('remediation_destination')
        incident.false_position = request.data.get('false_position', 'No')
        incident.ticket_relise = request.data.get('ticket_relise', 'No')
        
        # 2. Status ywalli Closed w nsajlou el wa9t
        incident.incident_status = 'Closed'
        incident.time_of_closed_incident = timezone.now()
        
        incident.save()

        # 3. Calcul MTTR (Mean Time To Resolve)
        diff = incident.time_of_closed_incident - incident.date_detection
        mttr_minutes = round(diff.total_seconds() / 60, 2)

        return Response({
            "message": "Incident clôturé",
            "status": incident.incident_status,
            "closed_at": incident.time_of_closed_incident,
            "mttr_minutes": mttr_minutes
        }, status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        """
        Action: Analyste yzid incident jdid b-ma3loumat awlia.
        Status automatique: 'Open'
        """
        data = request.data
        
        # 1. Ne5thou el ma3loumat mel Request
        titre = data.get('titre')
        date_detection = data.get('date_detection', timezone.now())
        insiter_typo = data.get('insiter_typo', 'Mineur')
        plant_name = data.get('plant_name')
        raised_by = data.get('raised_by')
        description_investigation = data.get('description_investigation')

        # 2. Validation sghira: Titre lezem ykoun mawjoud
        if not titre:
            return Response({"error": "Le titre est obligatoire"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Ensajlou fil Base de données
        # Nota: incident_id_formatted taw yitsna3 automatique fil models.save()
        incident = Incident.objects.create(
            titre=titre,
            date_detection=date_detection,
            insiter_typo=insiter_typo,
            plant_name=plant_name,
            raised_by=raised_by,
            description_investigation=description_investigation,
            incident_status='Open' # Dima yabda Open
        )

        # 4. Nrajj3ou el Resultat
        return Response({
            "message": "Incident créé avec succès",
            "incident_id": incident.incident_id_formatted,
            "id": incident.id_incident,
            "status": incident.incident_status
        }, status=status.HTTP_201_CREATED)




