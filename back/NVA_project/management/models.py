from django.db import models
from accounts.models import Agent
from django.conf import settings

class Event(models.Model):
    location = models.CharField(max_length=250)
    company_name = models.CharField(max_length=100)
    event_code = models.CharField(max_length=50, unique=True)
    agents = models.ManyToManyField('accounts.Agent', related_name='events')

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
