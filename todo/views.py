from rest_framework.views import APIView
from rest_framework.response import Response
from .ai_helper import ask_cyber_assistant
from rest_framework.permissions import AllowAny
class AIAdvisorView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        title = request.data.get('type', 'Tâche Générale')
        description = request.data.get('description', '')

        if not description:
            return Response({"error": "La description est nécessaire"}, status=400)

        suggestion = ask_cyber_assistant(title, description)
        return Response({"suggestion": suggestion})