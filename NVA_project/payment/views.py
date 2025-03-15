from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Payment
from accounts.models import Agent
from .serializers import PaymentSerializer, PaymentDetailSerializer, PaymentCreateSerializer

class PaymentListView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Liste tous les paiements.
        """
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

class PaymentDetailView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Récupère les détails d'un paiement spécifique.
        """
        payment = get_object_or_404(Payment, pk=pk)
        serializer = PaymentDetailSerializer(payment)
        return Response(serializer.data)

class CreatePaymentView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Crée un nouveau paiement.
        """
        serializer = PaymentCreateSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            
            # Récupérer l'agent pour inclure son nom d'utilisateur dans la réponse
            agent = Agent.objects.get(id=request.data['agent_id'])
            
            return Response({
                'id': payment.id,
                'username': agent.username,
                'amount': payment.amount,
                'work_days': payment.work_days,
                'total_payment': payment.total_payment,
                'created_at': payment.created_at
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AgentPaymentsView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def get(self, request, agent_id=None):
        """
        Récupère les paiements d'un agent spécifique ou de l'agent authentifié.
        """
        if agent_id:
            # Si un ID d'agent est fourni, récupérer les paiements de cet agent
            try:
                agent = Agent.objects.get(id=agent_id)
                payments = Payment.objects.filter(agent=agent)
            except Agent.DoesNotExist:
                return Response({"error": "Agent non trouvé."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Sinon, supposer que l'agent est l'utilisateur authentifié
            agent = request.user
            payments = Payment.objects.filter(agent=agent)
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

class AgentTotalPaymentView(APIView):
    #permission_classes = [IsAuthenticated]
    
    def get(self, request, agent_id=None):
        """
        Récupère le total des paiements d'un agent spécifique ou de l'agent authentifié.
        """
        if agent_id:
            # Si un ID d'agent est fourni, récupérer les paiements de cet agent
            try:
                agent = Agent.objects.get(id=agent_id)
            except Agent.DoesNotExist:
                return Response({"error": "Agent non trouvé."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Sinon, supposer que l'agent est l'utilisateur authentifié
            agent = request.user
        
        # Récupérer le dernier paiement pour obtenir le total
        latest_payment = Payment.objects.filter(agent=agent).order_by('-created_at').first()
        
        if latest_payment:
            total_payment = latest_payment.total_payment
        else:
            total_payment = 0
        
        # Calculer les statistiques
        total_credits = Payment.objects.filter(agent=agent, amount__gt=0).count()
        total_debits = Payment.objects.filter(agent=agent, amount__lt=0).count()
        
        return Response({
            'agent_id': agent.id,
            'agent_username': agent.username,
            'total_payment': total_payment,
            'total_credits': total_credits,
            'total_debits': total_debits
        })