import random
from urllib import request
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework import status,generics
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsAdminUser, IsAnalysteN1, IsAnalysteN2, IsManager
# Create your views here.
from audit.models import create_audit_log
from django.core.cache import cache # Lezem nzidou hedhi
import random
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

User = get_user_model()

class MyLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]  # Koul wahed ynajjem ylogin, besh nthabbet f'el
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)
            usere = authenticate(username=username, password=password)
            if not usere:
                return Response({"error": "Mot de passe incorrect."}, status=401)
            # 1. Thabbet fel Verification
            if not user.is_verified:
                return Response({"error": "Veuillez vérifier votre email d'abord."}, status=401)
            
            # 2. Thabbet fel Approval
            if not user.is_approved:
                return Response({"error": "Compte en attente d'approbation par l'admin."}, status=403)

            create_audit_log(
                user=user, 
                action='LOGIN', 
                description=f"L'utilisateur {user.username} s'est connecté au système."
            )
            # 3. Ken l'user mrigel, khalli SimpleJWT ythabbet f'el Password
            return super().post(request, *args, **kwargs)

        except User.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé."}, status=404)
class RegisterView(APIView): # Baddelneha APIView 3adia
    permission_classes = [AllowAny] # Koul wahed ynajjem yregister
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Nakhou el data ama MA NA3MELCH .save()
            user_data = serializer.validated_data
            if User.objects.filter(username=user_data['username']).exists():
                return Response({"error": "Le nom d'utilisateur est déjà pris."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check email unique
            if User.objects.filter(email=user_data['email']).exists():
                return Response({"error": "Cet email est déjà associé à un compte."}, status=status.HTTP_400_BAD_REQUEST)
            
            otp_code = str(random.randint(100000, 999999))
            
            # Nkhabiw el data f'el Cache mta3 Django (yeb9aw 15 dbi9a)
            # El Key hiya l'email, w el Value hiya el data mta3 l'user + el code
            cache_key = f"pending_user_{user_data['email']}"
            cache_data = {
                'user_data': user_data,
                'otp_code': otp_code
            }
            cache.set(cache_key, cache_data, timeout=900) # 900 seconds = 15 min

            # Nab3thou el email
            try:
                send_mail(
                    "Code de vérification",
                    f"Votre code est : {otp_code}",
                    settings.EMAIL_HOST_USER,
                    [user_data['email']]
                )
                return Response({"message": "Code envoyé à votre email. Le compte n'est pas encore créé."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": "Erreur d'envoi email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# view login jwt token
"""class MyLoginView(TokenObtainPairView): 
    
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        username = request.data.get('username')
        user = User.objects.get(username=username)
        
        if not user.is_approved:
            raise AuthenticationFailed("Compte mte3ek mazzal yestana f'el validation mta3 l'Admin.")
        if not user.is_verified:
            raise AuthenticationFailed("Lezem t-validi el code elli jék 3la el email.")
            
        return response"""
    


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]  # Koul wahed ynajjem yverify
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        cache_key = f"pending_user_{email}"
        cached_data = cache.get(cache_key)

        if not cached_data:
            return Response({"error": "Code expiré ou email invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if cached_data['otp_code'] == code:
            # El code s7i7! Tawa nasan3ou el User
            user_data = cached_data['user_data']
            
            # create_user bech el password yetshaffar
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                role=user_data.get('role', 'ANALYSTE_N1'),
                telephone=user_data.get('telephone', ''),
                is_active=True, 
                is_verified=True,  # <--- HEDHI EL NA9SA!
                is_approved=False
            )
            
            # N'faskhou el data mel cache khater t'sajlet
            cache.delete(cache_key)
            
            return Response({"message": "Compte créé avec succès! En attente de l'approbation de l'admin."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Code incorrect."}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            create_audit_log(
                user=request.user, 
                action='LOGIN', 
                description=f"L'utilisateur {request.user.username} s'est connecté au système."
            )
            token.blacklist() #supprime el token mel database mta3 blacklist
            return Response({"message":"Déconnexion réussie"},status=205)
        except Exception as e:
            return Response({"error":"Token invalide"},status=400)



class ProfileView(APIView):
    permission_classes = [IsAuthenticated,IsAnalysteN2|IsAdminUser|IsManager|IsAnalysteN1] 
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
