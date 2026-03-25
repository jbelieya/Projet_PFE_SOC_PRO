from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Count, ExpressionWrapper, F, Avg, DurationField,fields,Q
from .permissions import IsAdminUser, IsAnalysteN1, IsAnalysteN2, IsManager
from .models import Incident
from .serializers import IncidentSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from rest_framework.decorators import action
from django.utils import timezone
# Create your views here.
class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated,IsAnalysteN2|IsAdminUser|IsManager|IsAnalysteN1]  # Koul el actions mta3 el incidents ytalbou authentication
    # get all incidents: GET /api/incidents/
    def list(self, request, *args, **kwargs):
        """
        Action: Trajja3 liste mta3 les incidents kemlin.
        URL: GET /api/incidents/
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
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
        if request.user.is_authenticated:
            incident.user_name = request.user
        else:
      
            return Response(
            {"error": "Lazmek t-koun m-connecti bch t-a3mel Acknowledge"}, 
            status=403
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
    
    #modification de l'incident
    def update(self, request, *args, **kwargs):
        incident = self.get_object() # Hadhi hiya l-incident mta3ek (Single Object)

    # 1. Check Closure
        if incident.incident_status == 'Closed':
            return Response({"error": "Impossible de modifier un incident clôturé."}, status=400)

        if incident.user_name != request.user:
            return Response({'error': 'Vous n\'êtes pas l\'analyste assigné...'}, status=403)
    # 3. Update Fields
    # N-est-a3mlou .get() bch kén m-famech data, i-khali l-valeur l-9dima
        incident.titre = request.data.get('titre', incident.titre)
        incident.insiter_typo = request.data.get('insiter_typo', incident.insiter_typo)
        incident.plant_name = request.data.get('plant_name', incident.plant_name)
        incident.raised_by = request.data.get('raised_by', incident.raised_by)
        incident.description_investigation = request.data.get('description_investigation', incident.description_investigation)

    # 4. SAVE (Houni l-s7i7: update kén l-row hedha)
        incident.save()

        return Response({
        "message": "Incident modifié avec succès",
        "incident_id": incident.incident_id_formatted,
        "id": incident.id_incident,
        "status": incident.incident_status
    }, status=status.HTTP_200_OK)


    #KPIs de incidents ........ nouvelle action pour les KPIs
    # Fonction de filtrage (Moteur de recherche par date)
    def get_filtered_queryset(self, request):
        queryset = self.get_queryset()
        
        # Filtres de temps
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if year:
            queryset = queryset.filter(date_detection__year=year)
        if month:
            queryset = queryset.filter(date_detection__month=month)
            
        return queryset
    #KPI 1:calculer le MTTD (Mean Time To Detect) de tous les incidents
    @action(detail=False, methods=['get'])
    def mttd(self, request):
        queryset = self.get_queryset()
        data = queryset.annotate(
            diff=ExpressionWrapper(F('date_detection') - F('first_event'), output_field=DurationField())
        ).aggregate(avg=Avg('diff'))
        return Response({"mttd": self._duration_to_minutes(data['avg'])})
    #KPI 2: Calculer le MTTR (Mean Time To Resolve) de tous les incidents
    @action(detail=False, methods=['get'])
    def mttr(self, request):
        # Ici on filtre les incidents clôturés et on applique les filtres temporels
        queryset = self.get_filtered_queryset(request).filter(
            incident_status='Closed', 
            time_of_closed_incident__isnull=False
        )
        data = queryset.annotate(
            diff=ExpressionWrapper(F('time_of_closed_incident') - F('date_detection'), output_field=DurationField())
        ).aggregate(avg=Avg('diff'))
        return Response({"mttr": self._duration_to_minutes(data['avg'])})
    
    #KPI 3: Calculer le MTTA (Mean Time To Acknowledge) de tous les incidents
    @action(detail=False, methods=['get'])
    def mtta(self, request):
        queryset =Incident.objects.filter(acknowledge_time__isnull=False)
        mtta_data = queryset.annotate(
            diff_acknowledge=ExpressionWrapper(
                F('acknowledge_time') - F('date_detection'),
                output_field=DurationField()
            )
        ).aggregate(avg_mtta=Avg('diff_acknowledge'))

        return Response({
            "mtta": self._duration_to_minutes(mtta_data['avg_mtta'])   
        }, status=status.HTTP_200_OK)
    
    # KPI 4: Calculer le taux de faux positifs
    @action(detail=False, methods=['get'])
    def false_positive_rate(self, request):
        stat_type = request.query_params.get('type') # 'month' wala 'year'
        values_raw = request.query_params.get('values') # '1,2,3'
    
        if not stat_type or not values_raw:
            return Response({"error": "Type et values sont obligatoires"}, status=400)

    # N-7awlou '1,2,3' l-lista [1, 2, 3]
        try:
            values_list = [int(v.strip()) for v in values_raw.split(',')]
        except ValueError:
             return Response({"error": "Values must be numbers separated by commas"}, status=400)

        queryset = self.get_queryset()
        response_data = {}

        base_filter = Q(false_position='Yes', incident_status='Closed')

        if stat_type == 'month':
            current_year = timezone.now().year # 2026
            for m in values_list:
                count = queryset.filter(
                base_filter, 
                date_detection__year=current_year, 
                date_detection__month=m
                ).count()
                response_data[m] = count

        elif stat_type == 'year':
            for y in values_list:
                count = queryset.filter(
                base_filter, 
                date_detection__year=y
            ).count()
                response_data[y] = count

        return Response(response_data)
    # KPI 5: Nombre de true positives (Incidents réels)
    @action(detail=False, methods=['get'])
    def get_true_positives_stats(self, request):
   
        stat_type = request.query_params.get('type') # 'month' wala 'year'
        values_raw = request.query_params.get('values') # '1,2,3'
    
        if not stat_type or not values_raw:
            return Response({"error": "Type et values sont obligatoires"}, status=400)

    # N-7awlou '1,2,3' l-lista [1, 2, 3]
        try:
            values_list = [int(v.strip()) for v in values_raw.split(',')]
        except ValueError:
             return Response({"error": "Values must be numbers separated by commas"}, status=400)

        queryset = self.get_queryset()
        response_data = {}

    # Logic True Positive: false_position='No' w incident_status='Closed'
        base_filter = Q(false_position='No', incident_status='Closed')

        if stat_type == 'month':
            current_year = timezone.now().year # 2026
            for m in values_list:
                count = queryset.filter(
                base_filter, 
                date_detection__year=current_year, 
                date_detection__month=m
                ).count()
                response_data[m] = count

        elif stat_type == 'year':
            for y in values_list:
                count = queryset.filter(
                base_filter, 
                date_detection__year=y
            ).count()
                response_data[y] = count

        return Response(response_data)
    # KPI 6: Nombre Open Incidents
    # KPI 6: Nombre Open Incidents (Filtered by Month/Year)
    @action(detail=False, methods=['get'])
    def open_incidents_count(self, request):
        stat_type = request.query_params.get('type')  # 'month' wala 'year'
        values_raw = request.query_params.get('values')  # '1,2,3'
    
        if not stat_type or not values_raw:
            return Response({"error": "Type et values sont obligatoires"}, status=400)

        try:
            values_list = [int(v.strip()) for v in values_raw.split(',')]
        except ValueError:
            return Response({"error": "Values must be numbers separated by commas"}, status=400)

        queryset = self.get_queryset()
        response_data = {}

        # Logic: status 'Open'
        base_filter = Q(incident_status='Open')

        if stat_type == 'month':
            current_year = timezone.now().year
            for m in values_list:
                count = queryset.filter(
                    base_filter, 
                    date_detection__year=current_year, 
                    date_detection__month=m
                ).count()
                response_data[m] = count

        elif stat_type == 'year':
            for y in values_list:
                count = queryset.filter(
                    base_filter, 
                    date_detection__year=y
                ).count()
                response_data[y] = count

        return Response(response_data)

    # KPI 7: Nombre Closed Incidents (Filtered by Month/Year)
    @action(detail=False, methods=['get'])
    def closed_incidents_count(self, request):
        stat_type = request.query_params.get('type')
        values_raw = request.query_params.get('values')
    
        if not stat_type or not values_raw:
            return Response({"error": "Type et values sont obligatoires"}, status=400)

        try:
            values_list = [int(v.strip()) for v in values_raw.split(',')]
        except ValueError:
            return Response({"error": "Values must be numbers separated by commas"}, status=400)

        queryset = self.get_queryset()
        response_data = {}

        # Logic: status 'Closed'
        base_filter = Q(incident_status='Closed')

        if stat_type == 'month':
            current_year = timezone.now().year
            for m in values_list:
                count = queryset.filter(
                    base_filter, 
                    date_detection__year=current_year, 
                    date_detection__month=m
                ).count()
                response_data[m] = count

        elif stat_type == 'year':
            for y in values_list:
                count = queryset.filter(
                    base_filter, 
                    date_detection__year=y
                ).count()
                response_data[y] = count

        return Response(response_data)
    # KPI 8: Nombre alert par site (Filtered by Month/Year)
    @action(detail=False, methods=['get'])
    def incidents_by_site(self, request):
        return self._get_grouped_stats(request, 'plant_name')

    # KPI 9: Nombre alert par type (Filtered by Month/Year)
    @action(detail=False, methods=['get'])
    def incidents_by_type(self, request):
        return self._get_grouped_stats(request, 'severity_level')

    # KPI 11: Nombre alert par catégorie (Filtered by Month/Year)
    @action(detail=False, methods=['get'])
    def incidents_by_category(self, request):
        return self._get_grouped_stats(request, 'category')

    # KPI 12: Nombre alert par analyste (Filtered by Month/Year)
    @action(detail=False, methods=['get'])
    def incidents_by_analyst(self, request):
        return self._get_grouped_stats(request, 'user_name')

    # --- HELPER METHOD (Bch ma n-3awduch el code 100 marra) ---
    def _get_grouped_stats(self, request, group_field):
        stat_type = request.query_params.get('type')
        values_raw = request.query_params.get('values')

        if not stat_type or not values_raw:
            return Response({"error": "Type et values sont obligatoires"}, status=400)

        try:
            values_list = [int(v.strip()) for v in values_raw.split(',')]
        except ValueError:
            return Response({"error": "Values must be numbers"}, status=400)
        if group_field == 'user_name':
            group_field = 'user_name__username'
        queryset = self.get_queryset()
        response_data = {}
        
        if stat_type == 'month':
            current_year = timezone.now().year
            for m in values_list:
                # Group by the specific field for each month
                stats = queryset.filter(
                    date_detection__year=current_year, 
                    date_detection__month=m
                ).values(group_field).annotate(count=Count('id_incident'))
                
                # Format: { "1": [{"plant_name": "Site A", "count": 5}, ...], "2": [...] }
                response_data[m] = list(stats)

        elif stat_type == 'year':
            for y in values_list:
                stats = queryset.filter(
                    date_detection__year=y
                ).values(group_field).annotate(count=Count('id_incident'))
                
                response_data[y] = list(stats)

        return Response(response_data)
    # Helper function to convert duration to minutes
    def _duration_to_minutes(self, duration):
        if duration is None:
            return 0
        return round(duration.total_seconds() / 60, 2)
    

    #Rappore de incidents
    @action(detail=True, methods=['get'])
    def export_incident_pdf(self, request, pk=None):
    # 1. Recuperation mta' l-incident mel base
        try:
            incident = self.get_object()
        except Incident.DoesNotExist:
            return HttpResponse("Incident non trouvé", status=404)

    # 2. Preparation mta' l-Response PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Incident_{incident.incident_id_formatted}.pdf"'

    # 3. Create el Canvas
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter

    # --- Header Design ---
        p.setFillColor(colors.slategray)
        p.rect(0, height - 80, width, 80, fill=True, stroke=False)
    
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 20)
        p.drawString(40, height - 50, "SOC PLATFORM - INCIDENT REPORT")
    
    # --- Incident Details ---
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 12)
        y = height - 120
    
        details = [
        ("ID / REF:", f"{incident.incident_id_formatted}"),
        ("Titre:", f"{incident.titre}"),
        ("Status:", f"{incident.incident_status}"),
        ("Severity:", f"{incident.severity_level}"),
        ("Analyste:", f"{incident.user_name}"),
        ("Date Detection:", f"{incident.date_detection.strftime('%Y-%m-%d %H:%M')}"),
        ("Host Name:", f"{incident.host_name}"),
        ("Description:", f"{incident.description_investigation}"),
        ]

        for label, value in details:
            p.setFont("Helvetica-Bold", 11)
            p.drawString(50, y, label)
            p.setFont("Helvetica", 11)
            p.drawString(150, y, value)
            y -= 25  # Move to next line

    # --- Footer ---
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(40, 40, "Generé par COFICAB SOC Platform")

        p.showPage()
        p.save()
        return response