from django.utils import timezone
from django.db import models
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from accounts.models import Agent
from event.models import Event
from payment.models import Payment
from presence.models import Presence
from notification.models import Notification
from messaging.models import Message
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from rest_framework import status
import calendar
import datetime
import logging

logger = logging.getLogger(__name__)

class AdminDashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            # Récupérer le paramètre 'month' si fourni (format: YYYY-MM)
            month_str = request.query_params.get('month', None)
            if month_str:
                try:
                    year, month = map(int, month_str.split('-'))
                    month_date = datetime.date(year, month, 1)
                    _, days_in_month = calendar.monthrange(year, month)
                    month_end = datetime.date(year, month, days_in_month)
                except (ValueError, TypeError):
                    return Response({"error": "Format de mois invalide. Utilisez YYYY-MM"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Par défaut, utiliser le mois courant
                now = timezone.now().date()
                month_date = datetime.date(now.year, now.month, 1)
                _, days_in_month = calendar.monthrange(now.year, now.month)
                month_end = datetime.date(now.year, now.month, days_in_month)

            # Filtrer les données pour le mois spécifié
            thirty_days_ago = month_date - timedelta(days=30)

            # Statistiques des agents
            total_agents = Agent.objects.count()
            active_agents = Agent.objects.filter(
                events__start_date__gte=thirty_days_ago
            ).distinct().count()
            
            if active_agents == 0:
                active_agents = Agent.objects.filter(
                    payments__created_at__gte=thirty_days_ago
                ).distinct().count()
            
            if active_agents == 0:
                active_agents = total_agents

            # Statistiques des événements
            total_events = Event.objects.count()
            ongoing_events = Event.objects.filter(
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ).count()
            upcoming_events = Event.objects.filter(
                start_date__gt=timezone.now()
            ).count()

            # Statistiques des paiements
            total_payments = Payment.objects.filter(amount__gt=0).aggregate(
                total=models.Sum('amount')
            )['total'] or 0

            # Calcul du taux de présence pour le mois spécifié
            total_presences = Presence.objects.filter(
                timestamp__date__gte=month_date,
                timestamp__date__lte=month_end
            ).count()
            approved_presences = Presence.objects.filter(
                timestamp__date__gte=month_date,
                timestamp__date__lte=month_end,
                status='approved'
            ).count()
            presence_rate = (approved_presences / total_presences * 100) if total_presences > 0 else 0

            # Autres statistiques
            unread_notifications = Notification.objects.filter(is_read=False).count()
            unread_messages = Message.objects.filter(is_read=False).count()

            return Response({
                'total_agents': total_agents,
                'active_agents': active_agents,
                'total_events': total_events,
                'ongoing_events': ongoing_events,
                'upcoming_events': upcoming_events,
                'total_payments': float(total_payments),
                'presence_rate': round(presence_rate, 2),
                'unread_notifications': unread_notifications,
                'unread_messages': unread_messages
            })
        except Exception as e:
            logger.error(f"Error in AdminDashboardStatsView: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=500)

class PaymentChartDataView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            logger.info("Début de la récupération des données du graphique de paiement")
            total_payments = Payment.objects.count()
            print(f"Nombre total de paiements dans la base de données: {total_payments}")
            
            if total_payments == 0:
                logger.warning("Aucun paiement trouvé dans la base de données")
                return Response([], status=status.HTTP_200_OK)
            
            all_payments = list(Payment.objects.all().values('id', 'amount', 'created_at'))
            logger.info(f"Échantillon de paiements: {all_payments[:5]}")
            
            payments = Payment.objects.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                amount=Sum('amount')
            ).order_by('month')
            
            payments_list = list(payments)
            logger.info(f"Résultats de l'agrégation: {payments_list}")
            
            chart_data = []
            for payment in payments_list:
                month_name = calendar.month_abbr[payment['month'].month]
                chart_data.append({
                    'month': month_name,
                    'amount': abs(float(payment['amount']))
                })
            
            logger.info(f"Données du graphique formatées: {chart_data}")
            
            if len(chart_data) < 8:
                existing_data = {item['month']: item['amount'] for item in chart_data}
                all_months = [calendar.month_abbr[i] for i in range(1, 13)]
                final_chart_data = []
                for month in all_months:
                    if month in existing_data:
                        final_chart_data.append({'month': month, 'amount': existing_data[month]})
                    else:
                        final_chart_data.append({'month': month, 'amount': 0})
                
                chart_data = final_chart_data[:8]
            
            logger.info(f"Données finales du graphique: {chart_data}")
            return Response(chart_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données du graphique: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erreur lors de la récupération des données du graphique: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RecentEventsView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        try:
            now = timezone.now()
            recent_events = Event.objects.all().order_by('-start_date')[:5]
            events_data = []
            for event in recent_events:
                start_date = event.start_date
                if timezone.is_naive(start_date):
                    start_date = timezone.make_aware(start_date)
                
                end_date = event.end_date
                if timezone.is_naive(end_date):
                    end_date = timezone.make_aware(end_date)
                
                if start_date > now:
                    status = "upcoming"
                elif end_date < now:
                    status = "completed"
                else:
                    status = "ongoing"
                
                events_data.append({
                    'id': event.id,
                    'location': event.location,
                    'company_name': event.company_name,
                    'event_code': event.event_code,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'status': status,
                    'agents_count': event.agents.count()
                })
            
            return Response(events_data)
        except Exception as e:
            print(f"Error in RecentEventsView: {str(e)}")
            return Response({"error": str(e)}, status=500)

class RecentPaymentsView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        try:
            recent_payments = Payment.objects.all().order_by('-created_at')[:5]
            payments_data = []
            for payment in recent_payments:
                payments_data.append({
                    'id': payment.id,
                    'agent': payment.agent.username if payment.agent else "Agent inconnu",
                    'amount': float(payment.amount),
                    'work_days': payment.work_days,
                    'type': 'credit' if payment.amount >= 0 else 'debit',
                    'created_at': payment.created_at.isoformat()
                })
            
            return Response(payments_data)
        except Exception as e:
            print(f"Error in RecentPaymentsView: {str(e)}")
            return Response({"error": str(e)}, status=500)