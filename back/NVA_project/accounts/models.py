from django.db import models
from django.contrib.auth.models import AbstractUser

class Agent(AbstractUser):
    age = models.IntegerField(null=True,blank=True)
    gender = models.CharField(max_length=100,null=True,blank=True)
    location = models.CharField(max_length=250,null=True,blank=True)
    phone_number = models.CharField(max_length=15,null=True,blank=True)
    measurements = models.TextField(null=True,blank=True)
    total_payments = models.FloatField(default=0.0)  

    def __str__(self):
        return super().__str__()

class Photo(models.Model):
    agent = models.ForeignKey(Agent, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/')

    def __str__(self):
        return f"Photo for {self.agent.username}"
