from django.db import models
from django.utils import timezone
from accounts.models import Agent
from event.models import Event
import calendar
from django.db.models import Avg, Sum, Count, F, Q

class EventPerformance(models.Model):
    """Modèle pour stocker les données de performance liées à un événement"""
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='performance')
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    products_sold = models.IntegerField(default=0)
    client_satisfaction = models.IntegerField(default=0, choices=[
        (0, 'Non évalué'),
        (1, 'Insatisfait'),
        (2, 'Peu satisfait'),
        (3, 'Neutre'),
        (4, 'Satisfait'),
        (5, 'Très satisfait')
    ])
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Performance pour {self.event}"
    
    class Meta:
        verbose_name = "Performance d'événement"
        verbose_name_plural = "Performances d'événements"

class MonthlyRanking(models.Model):
    """Classement mensuel des agents"""
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='rankings')
    month = models.DateField()  # Premier jour du mois
    score = models.FloatField()
    rank = models.IntegerField()
    
    class Meta:
        unique_together = ('agent', 'month')
        ordering = ['rank']
    
    def __str__(self):
        return f"{self.agent.username} - {self.month.strftime('%B %Y')} - Rank: {self.rank}"

class AIAnalysis(models.Model):
    """Analyse IA des performances des agents"""
    month = models.DateField()  # Premier jour du mois
    analysis_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('month',)
        ordering = ['-month']
    
    def __str__(self):
        return f"AI Analysis - {self.month.strftime('%B %Y')}"
    
    @classmethod
    def get_month_data(cls, year, month):
        """Récupère les données de performance pour un mois spécifique"""
        month_date = timezone.datetime(year, month, 1).date()
        
        # Récupérer tous les agents actifs
        agents = Agent.objects.filter(is_active=True,is_superuser=False)
        
        # Calculer le nombre de jours dans le mois
        _, days_in_month = calendar.monthrange(year, month)
        month_end = timezone.datetime(year, month, days_in_month).date()
        
        performances = []
        for agent in agents:
            # Événements auxquels l'agent a participé ce mois-ci
            events = Event.objects.filter(
                agents=agent,
                start_date__year=year,
                start_date__month=month
            )
            
            # Nombre d'événements
            events_count = events.count()
            
            # Nombre de clients uniques (company_name)
            clients = events.values('company_name').distinct().count()
            
            # Revenus et produits vendus (depuis EventPerformance)
            revenue = 0
            products = 0
            for event in events:
                try:
                    perf = event.performance
                    revenue += float(perf.revenue)
                    products += perf.products_sold
                except EventPerformance.DoesNotExist:
                    pass
            
            # Taux de présence
            from presence.models import Presence
            total_days = Presence.objects.filter(
                agent=agent,
                timestamp__date__gte=month_date,
                timestamp__date__lte=month_end
            ).count()
            
            presence_rate = 0
            if total_days > 0:
                present_days = Presence.objects.filter(
                    agent=agent,
                    timestamp__date__gte=month_date,
                    timestamp__date__lte=month_end,
                    status='approved'
                ).count()
                presence_rate = round((present_days / total_days) * 100, 2)
            
            # Classement si disponible
            try:
                ranking = MonthlyRanking.objects.get(
                    agent=agent,
                    month__year=year,
                    month__month=month
                )
                score = ranking.score
                rank = ranking.rank
            except MonthlyRanking.DoesNotExist:
                score = 0
                rank = 0
            
            performances.append({
                "id": agent.id,
                "name": agent.username,
                "clients": clients,
                "products": products,
                "events": events_count,
                "presence_rate": presence_rate,
                "revenue": revenue,
                "score": score,
                "rank": rank
            })
        
        # Calculer les totaux de l'équipe
        team_totals = {
            "clients": sum(p["clients"] for p in performances),
            "products": sum(p["products"] for p in performances),
            "events": sum(p["events"] for p in performances),
            "revenue": sum(p["revenue"] for p in performances),
            "avg_presence": sum(p["presence_rate"] for p in performances) / len(performances) if performances else 0
        }
        
        return {
            "performances": performances,
            "team_totals": team_totals,
            "month_date": month_date
        }
