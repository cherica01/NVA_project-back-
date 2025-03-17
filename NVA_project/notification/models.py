

# Create your models here.
from django.db import models
from accounts.models import Agent

class Notification(models.Model):
    recipient = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    date = models.DateField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification pour {self.recipient.username}: {self.message[:30]}..."
    
    class Meta:
        ordering = ['-created_at']