from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import StreamingHttpResponse
from .ai_helper import ask_cyber_assistant_stream # Thabet f-ism el function el jdida

class AIAdvisorView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        title = request.data.get('type', 'Tâche Générale')
        description = request.data.get('description', '')

        # 1. Na3mlou Generator function dekhel el post
        def stream_generator():
            # ask_cyber_assistant_stream lezem ykoun fiha "stream=True" w "yield"
            for word in ask_cyber_assistant_stream(title, description):
                yield word 

        # 2. N-raj3ou el StreamingHttpResponse direct
        return StreamingHttpResponse(stream_generator(), content_type='text/plain')