from rest_framework import serializers
from .models import Agent 



class AgentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['username','password','age','gender','location','phone_number','measurements']
        extra_kwargs = {'password':{'write_only':True}}
    def create(self, validate_data):
        password = validate_data.pop('password')
        agent = Agent(**validate_data)
        agent.set_password(password)
        agent.save()
        return agent 
