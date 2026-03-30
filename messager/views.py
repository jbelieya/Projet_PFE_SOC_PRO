
from django.http import HttpResponse
from django.http import HttpResponse
from django.shortcuts import render
import ast

from messager import permission
from .models import ChatView, User
from .serializers import ChatViewSerializer
from django.conf import settings
from rest_framework import viewsets
from accounts.serializers import UserSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken, Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication # 1. Importi hedhi
from rest_framework.permissions import IsAuthenticated
# Create your views here.



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all() 
    serializer_class = UserSerializer
    
    # 2. Baddel TokenAuthentication b-JWTAuthentication
    authentication_classes = [JWTAuthentication] 
    
    # 3. Raja3 el permissions bech mouch ay wa7ed i-chouf el analysts
    permission_classes = [IsAuthenticated]

class ChatViewSet(viewsets.ModelViewSet):
    queryset = ChatView.objects.all()
    serializer_class = ChatViewSerializer
    
    # 4. Nafs el 7aja hna
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })
@csrf_exempt
def create_new_chat(request):
    if request.method == 'POST':
        querydictstr = request.body.decode('utf-8')
        querydict = ast.literal_eval(querydictstr)
        ChatView.create_chat(querydict['textcontent'],querydict['sender'], querydict['receiver'])
    return HttpResponse("hello world")

