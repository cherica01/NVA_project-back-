from rest_framework import serializers
from .models import Notification, Payment

class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True) 

    class Meta:
        model = Notification
        fields = ['message', 'date', 'recipient','sender_username']
        
        

class PaymentSerializer(serializers.ModelSerializer):
    total_payment = serializers.FloatField(read_only=True)
    payment_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)  # Format lisible

    class Meta:
        model = Payment
        fields = ['agent', 'work_days', 'amount', 'total_payment', 'payment_date']