
from rest_framework.authtoken.models import Token
from django.http import HttpResponse
from django.http import HttpResponse
from django.shortcuts import render
import ast
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from messager import permission
from .models import ChatView
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
from django.contrib.auth import get_user_model 
User = get_user_model() # 2. Get the custom user model
# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all() 
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication] 
    
    permission_classes = [IsAuthenticated]

class ChatViewSet(viewsets.ModelViewSet):
    queryset = ChatView.objects.all()
    serializer_class = ChatViewSerializer
    
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

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_conversation(request, other_user_id):
    current_user = request.user
    
    messages = ChatView.objects.filter(
        Q(sender=current_user, receiver_id=other_user_id) |
        Q(sender_id=other_user_id, receiver=current_user)
    ).order_by('sent_date')
    
    serializer = ChatViewSerializer(messages, many=True)
    return Response(serializer.data)