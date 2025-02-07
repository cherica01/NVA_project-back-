from rest_framework import serializers
from .models import Agent 


class AgentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['id', 'username', 'age', 'gender', 'location', 'phone_number', 'measurements','date_joined','is_superuser']
        read_only_fields = ['date_joined']
    def create(self, validated_data):
        password = validated_data.pop('password', None)  # Gère les cas où `password` est absent
        agent = Agent(**validated_data)
        if password:  # Si un mot de passe est fourni ou généré
            agent.set_password(password)
        agent.save()
        return agent
