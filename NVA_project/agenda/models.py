from django.db import models
from django.conf import settings
from event.models import Event

class AgentAvailability(models.Model):
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    is_available = models.BooleanField(default=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('agent', 'date')
        verbose_name_plural = 'Agent availabilities'
    
    def __str__(self):
        status = "disponible" if self.is_available else "non disponible"
        return f"{self.agent.username} - {self.date} - {status}"

class AgentPreference(models.Model):
    agent = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    preferred_locations = models.TextField(blank=True, null=True, help_text="Emplacements préférés séparés par des virgules")
    preferred_event_types = models.TextField(blank=True, null=True, help_text="Types d'événements préférés séparés par des virgules")
    max_events_per_week = models.PositiveIntegerField(default=5)
    max_events_per_month = models.PositiveIntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Préférences de {self.agent.username}"