from datetime import datetime
from django.db import models
from accounts.models import Agent
from django.conf import settings

class Event(models.Model):
    location = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    event_code = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    agents = models.ManyToManyField('accounts.Agent', related_name='events') 

  

    def is_agent_available(self, agent):
        # Vérification des dates de l'événement actuel
        start_datetime = self.start_date if isinstance(self.start_date, datetime) else datetime.combine(self.start_date, time.min)
        end_datetime = self.end_date if isinstance(self.end_date, datetime) else datetime.combine(self.end_date, time.max)
        
        # Vérification des dates des événements de l'agent
        for event in agent.events.all():
            agent_start = event.start_date if isinstance(event.start_date, datetime) else datetime.combine(event.start_date, time.min)
            agent_end = event.end_date if isinstance(event.end_date, datetime) else datetime.combine(event.end_date, time.max)

            if (start_datetime <= agent_end and end_datetime >= agent_start):
                return False
        return True

        
class Attendance(models.Model):
    agent = models.ForeignKey('accounts.Agent', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    photo = models.ImageField(upload_to='attendance_photos/')

class Payment(models.Model):
    agent = models.ForeignKey('accounts.Agent', on_delete=models.CASCADE, related_name='payments')
    work_days = models.IntegerField()
    amount = models.FloatField()
    payment_date = models.DateTimeField(auto_now_add=True)
    @property
    def total_payment(self):
        return self.work_days * self.amount

class Notification(models.Model):
    message = models.TextField()
    date = models.DateField()
    recipient = models.ForeignKey('accounts.Agent', on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications')
