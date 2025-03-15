from django.db import models

# Create your models here.
from django.db import models
from accounts.models import Agent
from django.core.validators import FileExtensionValidator

class Presence(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    )
    
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='presences')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Présence de {self.agent.username} le {self.timestamp.strftime('%d/%m/%Y à %H:%M')}"
    
    class Meta:
        ordering = ['-timestamp']

class PresencePhoto(models.Model):
    presence = models.ForeignKey(Presence, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(
        upload_to='presence_photos/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Photo pour {self.presence}"