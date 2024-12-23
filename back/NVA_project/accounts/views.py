from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AgentSerializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .models import Agent
from rest_framework.permissions import IsAuthenticated

class AddAgentView(APIView):
    permission_classes = [IsAuthenticated]  # Assurez-vous que l'utilisateur est authentifié

    def post(self, request):
        # Vérifiez si l'utilisateur est un super utilisateur
        if not request.user.is_superuser:
            return Response(
                {"detail": "Permission denied. Only superusers can add agents."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AgentSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AgentLoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Authentifier l'agent
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Générer le token et le refresh token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Sérialiser les informations de base de l'agent
            agent = Agent.objects.get(username=username)
            serializer = AgentSerializers(agent)

            # Retourner les informations de base et les tokens
            return Response({
                'user': serializer.data,
                'access_token': access_token,
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class AgentUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # S'assurer que l'utilisateur est authentifié

    def get_object(self, pk):
        """ Récupère l'agent à partir de l'ID (pk) """
        try:
            return Agent.objects.get(pk=pk)
        except Agent.DoesNotExist:
            return None

    def patch(self, request, pk, *args, **kwargs):
        """ Met à jour partiellement un agent """
        instance = self.get_object(pk)
        if not instance:
            return Response({"detail": "Agent not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifiez si l'utilisateur authentifié est bien le propriétaire de l'agent
        if request.user != instance:  # Comparer l'utilisateur authentifié avec l'instance de l'agent
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        # Sérialisation et validation des données envoyées pour la mise à jour partielle
        serializer = AgentSerializers(instance, data=request.data, partial=True)
        if serializer.is_valid():
            # Sauvegarder l'agent mis à jour
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Si la validation échoue, retourner les erreurs
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class AgentDeleteView(APIView):
    permission_classes = [IsAuthenticated]  # S'assurer que l'utilisateur est authentifié

    def get_object(self, pk):
        """ Récupère l'agent à partir de l'ID (pk) """
        try:
            return Agent.objects.get(pk=pk)
        except Agent.DoesNotExist:
            return None

    def delete(self, request, pk, *args, **kwargs):
        """ Supprime un agent si l'utilisateur est autorisé """
        instance = self.get_object(pk)
        if not instance:
            return Response({"detail": "Agent not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifiez si l'utilisateur authentifié est bien le propriétaire de l'agent
        if request.user != instance:  # Comparer l'utilisateur authentifié avec l'instance de l'agent
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        # Supprimer l'agent
        instance.delete()
        return Response({"detail": "Agent account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # Limite l'accès aux utilisateurs connectés

    def get(self, request):
        # Utilise l'utilisateur connecté (request.user)
        agent = request.user
        serializer = AgentSerializers(agent)
        return Response(serializer.data, status=status.HTTP_200_OK)