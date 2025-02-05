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
from rest_framework.permissions import IsAdminUser
import random
import string
class AgentListView(APIView):
    permission_classes = [IsAuthenticated]  # Restreindre l'accès aux utilisateurs authentifiés

    def get(self, request, format=None):
        agents = Agent.objects.filter(is_superuser=False)  # Récupère tous les agents
        serializer = AgentSerializers(agents, many=True)  # Sérialise la liste des agents
        return Response(serializer.data, status=status.HTTP_200_OK)  # Renvoie les données sérialisées


class RegeneratePasswordView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, agent_id):
        try:
            agent = Agent.objects.get(id=agent_id)
            new_password = generate_password()
            agent.set_password(new_password)
            agent.save()

            return Response({"password": new_password}, status=status.HTTP_200_OK)
        except Agent.DoesNotExist:
            return Response({"error": "Agent non trouvé."}, status=status.HTTP_404_NOT_FOUND)
def generate_password():
    """
    Génère un mot de passe de 8 caractères contenant :
    - Au moins une lettre majuscule
    - Au moins une lettre minuscule
    - Un chiffre
    - Les autres caractères étant des lettres aléatoires
    """
    # Assurez-vous qu'il y a au moins une lettre majuscule, une lettre minuscule et un chiffre
    uppercase = random.choice(string.ascii_uppercase)  # Une lettre majuscule
    lowercase = random.choice(string.ascii_lowercase)  # Une lettre minuscule
    digit = random.choice(string.digits)              # Un chiffre

    # Complétez avec des lettres aléatoires pour atteindre 8 caractères
    remaining = random.choices(string.ascii_letters, k=5)  # Lettres majuscules ou minuscules

    # Mélangez les caractères pour éviter un ordre prévisible
    password_list = list(uppercase + lowercase + digit + ''.join(remaining))
    random.shuffle(password_list)

    # Retournez le mot de passe final sous forme de chaîne
    return ''.join(password_list)

class AddAgentView(APIView):
    permission_classes = [IsAdminUser]  # Accessible uniquement aux administrateurs

    def post(self, request):
        # Copiez les données de la requête pour les modifier
        data = request.data.copy()

        # Générez un mot de passe conforme aux critères
        data['password'] = generate_password()

        # Sérialisez les données
        serializer = AgentSerializers(data=data)
        if serializer.is_valid():
            # Enregistrez l'agent et générez une réponse
            serializer.save()
            response_data = serializer.data
            response_data['password'] = data['password']  # Incluez le mot de passe dans la réponse
            return Response(response_data, status=status.HTTP_201_CREATED)

        # En cas d'erreur, retournez les erreurs de validation
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
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        """Récupère l'agent à partir de l'ID (pk)."""
        try:
            return Agent.objects.get(pk=pk)
        except Agent.DoesNotExist:
            return None

    def patch(self, request, pk, *args, **kwargs):
        """Met à jour partiellement un agent."""
        instance = self.get_object(pk)
        if not instance:
            return Response({"detail": "Agent not found."}, status=status.HTTP_404_NOT_FOUND)

        # Sérialisation et validation des données envoyées pour la mise à jour partielle
        serializer = AgentSerializers(instance, data=request.data, partial=True)
        if serializer.is_valid():
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
       # if request.user != instance:  # Comparer l'utilisateur authentifié avec l'instance de l'agent
           # return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

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