from django.db import models
from accounts.models import Agent

class Event(models.Model):
    location = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    event_code = models.CharField(max_length=50, unique=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    agents = models.ManyToManyField(Agent, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} - {self.event_code}"
    
    class Meta:
        ordering = ['-start_date']