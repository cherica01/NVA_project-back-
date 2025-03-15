from rest_framework import serializers
from .models import Payment
from accounts.models import Agent

class PaymentSerializer(serializers.ModelSerializer):
    agent = serializers.StringRelatedField()
    
    class Meta:
        model = Payment
        fields = ['id', 'agent', 'amount', 'work_days', 'total_payment', 'description', 'created_at']

class PaymentDetailSerializer(serializers.ModelSerializer):
    agent = serializers.StringRelatedField()
    
    class Meta:
        model = Payment
        fields = ['id', 'agent', 'amount', 'work_days', 'total_payment', 'description', 'created_at', 'updated_at']

class PaymentCreateSerializer(serializers.ModelSerializer):
    agent_id = serializers.IntegerField()
    
    class Meta:
        model = Payment
        fields = ['agent_id', 'amount', 'work_days', 'description']
    
    def validate_agent_id(self, value):
        try:
            Agent.objects.get(id=value)
        except Agent.DoesNotExist:
            raise serializers.ValidationError("Agent non trouvé.")
        return value
    
    def validate_amount(self, value):
        # Assurez-vous que le montant n'est pas zéro
        if value == 0:
            raise serializers.ValidationError("Le montant ne peut pas être zéro.")
        return value
    
    def validate_work_days(self, value):
        # Pour les débits, les jours de travail peuvent être zéro
        # Pour les crédits, les jours de travail doivent être positifs
        if self.initial_data.get('amount', 0) > 0 and value <= 0:
            raise serializers.ValidationError("Les jours de travail doivent être positifs pour un crédit.")
        return value
    
    def create(self, validated_data):
        agent_id = validated_data.pop('agent_id')
        agent = Agent.objects.get(id=agent_id)
        
        # Calculer le total des paiements précédents
        previous_payments = Payment.objects.filter(agent=agent)
        previous_total = sum(payment.amount for payment in previous_payments)
        
        # Créer le nouveau paiement
        payment = Payment.objects.create(
            agent=agent,
            total_payment=previous_total + validated_data['amount'],
            **validated_data
        )
        
        return payment