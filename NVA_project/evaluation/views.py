from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
import datetime
import calendar
import google.generativeai as genai
from django.conf import settings
import json
import csv
from django.http import HttpResponse

from .models import EventPerformance, MonthlyRanking, AIAnalysis
from .serializers import (
    EventPerformanceSerializer,
    AgentPerformanceSerializer,
    MonthlyRankingSerializer,
    AIAnalysisSerializer,
    PresenceStatSerializer
)
from accounts.models import Agent
from presence.models import Presence
from event.models import Event

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

class EventPerformanceViewSet(viewsets.ModelViewSet):
    """API pour gérer les performances des événements"""
    queryset = EventPerformance.objects.all()
    serializer_class = EventPerformanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = EventPerformance.objects.all()
        
        # Filtrer par événement si spécifié
        event_id = self.request.query_params.get('event_id', None)
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        # Filtrer par mois si spécifié
        month = self.request.query_params.get('month', None)
        if month:
            try:
                year, month = map(int, month.split('-'))
                queryset = queryset.filter(
                    event__start_date__year=year,
                    event__start_date__month=month
                )
            except (ValueError, TypeError):
                pass
        
        return queryset

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agent_performances(request):
    """Récupère les performances des agents pour un mois donné"""
    month_str = request.query_params.get('month', None)
    
    if month_str:
        try:
            year, month = map(int, month_str.split('-'))
            month_date = datetime.date(year, month, 1)
        except (ValueError, TypeError):
            return Response({"error": "Format de mois invalide. Utilisez YYYY-MM"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        today = timezone.now().date()
        month_date = datetime.date(today.year, today.month, 1)
    
    agents = Agent.objects.filter(is_active=True,is_superuser=False)
    serializer = AgentPerformanceSerializer(agents, many=True, context={'month': month_date, 'request': request})
    
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_monthly_rankings(request):
    """Récupère les classements mensuels des agents"""
    month_str = request.query_params.get('month', None)
    
    if month_str:
        try:
            year, month = map(int, month_str.split('-'))
            month_date = datetime.date(year, month, 1)
        except (ValueError, TypeError):
            return Response({"error": "Format de mois invalide. Utilisez YYYY-MM"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        today = timezone.now().date()
        month_date = datetime.date(today.year, today.month, 1)
    
    rankings = MonthlyRanking.objects.filter(
        month__year=month_date.year,
        month__month=month_date.month,
        agent__is_superuser=False
    ).order_by('rank')
    
    serializer = MonthlyRankingSerializer(rankings, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_presence_stats(request):
    """Récupère les statistiques de présence pour un mois donné"""
    month_str = request.query_params.get('month', None)
    agent_id = request.query_params.get('agent_id', None)
    
    if month_str:
        try:
            year, month = map(int, month_str.split('-'))
            month_date = datetime.date(year, month, 1)
            
            # Calculer le dernier jour du mois
            _, days_in_month = calendar.monthrange(year, month)
            month_end = datetime.date(year, month, days_in_month)
        except (ValueError, TypeError):
            return Response({"error": "Format de mois invalide. Utilisez YYYY-MM"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        today = timezone.now().date()
        month_date = datetime.date(today.year, today.month, 1)
        
        # Calculer le dernier jour du mois
        _, days_in_month = calendar.monthrange(today.year, today.month)
        month_end = datetime.date(today.year, today.month, days_in_month)
    
    query = Q(timestamp__date__gte=month_date, timestamp__date__lte=month_end)
    
    if agent_id:
        query &= Q(agent_id=agent_id)
    
    presence_stats = Presence.objects.filter(query).values('status').annotate(
        count=Count('id')
    )
    
    total = sum(stat['count'] for stat in presence_stats)
    
    if total > 0:
        for stat in presence_stats:
            stat['percentage'] = round((stat['count'] / total) * 100, 2)
    
    serializer = PresenceStatSerializer(presence_stats, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_ai_analysis(request):
    """Récupère ou génère une analyse IA des performances des agents"""
    month_str = request.query_params.get('month', None)
    force_refresh = request.query_params.get('refresh', 'false').lower() == 'true'
    
    if month_str:
        try:
            year, month = map(int, month_str.split('-'))
            month_date = datetime.date(year, month, 1)
        except (ValueError, TypeError):
            return Response({"error": "Format de mois invalide. Utilisez YYYY-MM"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        today = timezone.now().date()
        month_date = datetime.date(today.year, today.month, 1)
    
    # Vérifier si une analyse existe déjà pour ce mois
    if not force_refresh:
        try:
            analysis = AIAnalysis.objects.get(
                month__year=month_date.year,
                month__month=month_date.month
            )
            serializer = AIAnalysisSerializer(analysis)
            return Response(serializer.data)
        except AIAnalysis.DoesNotExist:
            pass
    
    # Générer une nouvelle analyse avec Gemini
    try:
        month_data = AIAnalysis.get_month_data(month_date.year, month_date.month)
        analysis_data = generate_ai_analysis(month_data)
        
        # Sauvegarder ou mettre à jour l'analyse
        analysis, created = AIAnalysis.objects.update_or_create(
            month=month_date,
            defaults={'analysis_json': analysis_data}
        )
        
        serializer = AIAnalysisSerializer(analysis)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def generate_ai_analysis(month_data):
    """Génère une analyse IA des performances des agents avec Gemini Flash 1.5"""
    performances = month_data["performances"]
    team_totals = month_data["team_totals"]
    month_date = month_data["month_date"]
    
    # Préparer les données pour Gemini
    month_name = calendar.month_name[month_date.month]
    year = month_date.year
    
    prompt = f"""
    Tu es un assistant IA spécialisé dans l'analyse des performances des agents pour une entreprise d'événementiel.
    
    Voici les données de performance pour {month_name} {year}:
    
    {json.dumps(performances, indent=2)}
    
    Totaux de l'équipe:
    {json.dumps(team_totals, indent=2)}
    
    En te basant sur ces données, fournis une analyse complète au format JSON avec la structure suivante:
    
    {{
      "top_performer": {{
        "name": "Nom de l'agent",
        "highlights": ["Réalisation clé 1", "Réalisation clé 2", "Réalisation clé 3"],
        "improvement_areas": ["Domaine 1", "Domaine 2"]
      }},
      "team_insights": {{
        "strengths": ["Force 1", "Force 2", "Force 3"],
        "challenges": ["Défi 1", "Défi 2"],
        "trends": ["Tendance 1", "Tendance 2"]
      }},
      "recommendations": [
        "Recommandation 1",
        "Recommandation 2",
        "Recommandation 3"
      ]
    }}
    
    Assure-toi que ton analyse est basée sur les données, spécifique et exploitable. Concentre-toi sur l'identification des modèles, des performances exceptionnelles et des domaines à améliorer.
    Réponds UNIQUEMENT avec l'objet JSON, sans texte supplémentaire.
    """
    
    # Appeler Gemini Flash 1.5
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    try:
        # Analyser la réponse pour s'assurer qu'elle est en JSON valide
        analysis_json = json.loads(response.text)
        return analysis_json
    except json.JSONDecodeError:
        # Si Gemini ne renvoie pas un JSON valide, créer une réponse par défaut
        return {
            "error": "Impossible de générer une analyse valide",
            "raw_response": response.text,
            "top_performer": {
                "name": performances[0]["name"] if performances else "Inconnu",
                "highlights": ["A généré le plus de revenus", "Excellent en acquisition de clients", "Taux de présence élevé"],
                "improvement_areas": ["Pourrait améliorer les ventes de produits", "Considérer des types d'événements plus diversifiés"]
            },
            "team_insights": {
                "strengths": ["Bonne performance globale", "Forte génération de revenus"],
                "challenges": ["Taux de présence incohérents", "Performance variable des ventes de produits"],
                "trends": ["Augmentation de l'acquisition de clients", "Croissance des revenus d'un mois à l'autre"]
            },
            "recommendations": [
                "Mettre en place une formation d'équipe sur les techniques de vente de produits",
                "Reconnaître et récompenser la présence constante",
                "Partager les meilleures pratiques des meilleurs performeurs avec l'équipe"
            ]
        }

@api_view(['POST'])
@permission_classes([IsAdminUser])
def calculate_monthly_rankings(request):
    """Calcule et enregistre les classements mensuels des agents"""
    month_str = request.data.get('month', None)
    
    if month_str:
        try:
            year, month = map(int, month_str.split('-'))
            month_date = datetime.date(year, month, 1)
        except (ValueError, TypeError):
            return Response({"error": "Format de mois invalide. Utilisez YYYY-MM"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        today = timezone.now().date()
        month_date = datetime.date(today.year, today.month, 1)
    
    # Récupérer tous les agents actifs
    agents = Agent.objects.filter(is_active=True,is_superuser=False)
    
    # Calculer les scores pour chaque agent
    rankings = []
    for agent in agents:
        # Récupérer les événements de l'agent pour ce mois
        events = Event.objects.filter(
            agents=agent,
            start_date__year=month_date.year,
            start_date__month=month_date.month
        )
        
        # Nombre de clients uniques
        clients = events.values('company_name').distinct().count()
        
        # Revenus et produits vendus
        revenue = 0
        products = 0
        for event in events:
            try:
                perf = event.performance
                revenue += float(perf.revenue)
                products += perf.products_sold
            except EventPerformance.DoesNotExist:
                pass
        
        # Nombre d'événements
        events_count = events.count()
        
        # Calculer le nombre de jours dans le mois
        _, days_in_month = calendar.monthrange(month_date.year, month_date.month)
        month_end = datetime.date(month_date.year, month_date.month, days_in_month)
        
        # Taux de présence
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
            presence_rate = (present_days / total_days) * 100
        
        # Calculer le score (moyenne pondérée des métriques normalisées)
        # Ceci est un algorithme de scoring simple - vous pouvez ajuster les poids selon vos besoins
        score = (
            (clients * 10) +           # 10 points par client
            (products * 4) +           # 2 points par produit
            (events_count * 5) +       # 5 points par événement
            (presence_rate * 0.5) +    # 0.5 point par pourcentage de présence
            (float(revenue) * 0.01)    # 0.01 point par euro de revenu
        )
        
        rankings.append({
            'agent': agent,
            'score': round(score, 2)
        })
    
    # Trier par score en ordre décroissant
    rankings.sort(key=lambda x: x['score'], reverse=True)
    
    # Attribuer les rangs et sauvegarder
    for i, ranking in enumerate(rankings):
        rank = i + 1
        MonthlyRanking.objects.update_or_create(
            agent=ranking['agent'],
            month=month_date,
            defaults={
                'score': ranking['score'],
                'rank': rank
            }
        )
    
    return Response({"message": f"Classements calculés pour {month_date.strftime('%B %Y')}"})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def export_performance_csv(request):
    """Exporte les données de performance au format CSV"""
    month_str = request.query_params.get('month', None)
    
    if month_str:
        try:
            year, month = map(int, month_str.split('-'))
            month_date = datetime.date(year, month, 1)
        except (ValueError, TypeError):
            return Response({"error": "Format de mois invalide. Utilisez YYYY-MM"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        today = timezone.now().date()
        month_date = datetime.date(today.year, today.month, 1)
    
    # Créer une réponse HTTP avec le type de contenu CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="agent_performance_{month_date.strftime("%Y_%m")}.csv"'
    
    # Créer un writer CSV
    writer = csv.writer(response)
    
    # Écrire l'en-tête
    writer.writerow(['ID', 'Nom', 'Clients', 'Produits', 'Événements', 'Taux de présence', 'Revenus', 'Score', 'Rang'])
    
    # Récupérer les données de performance
    month_data = AIAnalysis.get_month_data(month_date.year, month_date.month)
    performances = month_data["performances"]
    
    # Écrire les données
    for perf in performances:
        writer.writerow([
            perf["id"],
            perf["name"],
            perf["clients"],
            perf["products"],
            perf["events"],
            perf["presence_rate"],
            perf["revenue"],
            perf["score"],
            perf["rank"]
        ])
    
    return response
