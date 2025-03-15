from django.db import models
from accounts.models import Agent

class Payment(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    work_days = models.PositiveIntegerField(default=0)
    total_payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculer le paiement total si ce n'est pas déjà fait
        if self.total_payment is None:
            # Récupérer le total des paiements précédents
            previous_payments = Payment.objects.filter(agent=self.agent)
            previous_total = sum(payment.amount for payment in previous_payments)
            self.total_payment = previous_total + self.amount
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Paiement de {self.amount} pour {self.agent.username}"
    
    class Meta:
        ordering = ['-created_at']