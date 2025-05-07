"""
Utilitaires pour le chatbot - Fonctions de récupération et formatage des données
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Sum, Case, When, Value, IntegerField, Count
from django.core.exceptions import ObjectDoesNotExist

# Configurez le logger pour ce module
logger = logging.getLogger(__name__)

# ===== FONCTIONS POUR LES ÉVÉNEMENTS =====

def get_upcoming_events(user, days=7, limit=5):
    """
    Récupère les événements à venir.
    Pour un admin, récupère tous les événements. Pour un agent, seulement ses événements.
    """
    try:
        from agenda.models import Event
        
        today = timezone.now().date()
        end_date = today + timedelta(days=days)
        
        if user.is_superuser or user.is_staff:
            upcoming_events = Event.objects.filter(
                start_date__date__gte=today,
                start_date__date__lte=end_date
            ).select_related().prefetch_related('agents').order_by('start_date')[:limit]
        else:
            upcoming_events = Event.objects.filter(
                Q(agents=user),
                start_date__date__gte=today,
                start_date__date__lte=end_date
            ).select_related().prefetch_related('agents').order_by('start_date')[:limit]
        
        return upcoming_events
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des événements: {str(e)}")
        return []

def get_event_details(event_id, user):
    """
    Récupère les détails d'un événement spécifique.
    Pour un admin, accès à tous les événements. Pour un agent, vérifier l'autorisation.
    """
    if not isinstance(event_id, int) or event_id <= 0:
        logger.warning(f"ID d'événement invalide: {event_id}")
        return None
    
    try:
        from agenda.models import Event
        
        if user.is_superuser or user.is_staff:
            event = Event.objects.get(id=event_id)
        else:
            event = Event.objects.filter(
                id=event_id,
                agents=user
            ).first()
        
        return event
    
    except ObjectDoesNotExist:
        logger.warning(f"Événement {event_id} non trouvé ou non autorisé")
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'événement {event_id}: {str(e)}")
        return None

def get_events_by_location(user, location, days=30, limit=5):
    """
    Récupère les événements à un emplacement spécifique.
    """
    try:
        from agenda.models import Event
        
        today = timezone.now().date()
        end_date = today + timedelta(days=days)
        
        if user.is_superuser or user.is_staff:
            events = Event.objects.filter(
                location__icontains=location,
                start_date__date__gte=today,
                start_date__date__lte=end_date
            ).select_related().prefetch_related('agents').order_by('start_date')[:limit]
        else:
            events = Event.objects.filter(
                Q(agents=user),
                location__icontains=location,
                start_date__date__gte=today,
                start_date__date__lte=end_date
            ).select_related().prefetch_related('agents').order_by('start_date')[:limit]
        
        return events
    
    except Exception as e:
        logger.error(f"Erreur lors de la recherche d'événements par emplacement: {str(e)}")
        return []

def get_next_event(user):
    """
    Récupère le prochain événement.
    """
    try:
        from agenda.models import Event
        
        today = timezone.now().date()
        
        if user.is_superuser or user.is_staff:
            next_event = Event.objects.filter(
                start_date__date__gte=today
            ).select_related().prefetch_related('agents').order_by('start_date').first()
        else:
            next_event = Event.objects.filter(
                Q(agents=user),
                start_date__date__gte=today
            ).select_related().prefetch_related('agents').order_by('start_date').first()
        
        return next_event
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du prochain événement: {str(e)}")
        return None

def get_total_events(user, days=None):
    """
    Récupère le nombre total d'événements.
    Si days est spécifié, limite aux événements dans cette période.
    """
    try:
        from agenda.models import Event
        
        query = Event.objects.all()
        
        if days:
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=days)
            query = query.filter(
                start_date__date__gte=start_date,
                start_date__date__lte=end_date
            )
        
        if not (user.is_superuser or user.is_staff):
            query = query.filter(Q(agents=user))
        
        total = query.count()
        return {'total_events': total, 'days': days if days else 'tous les temps'}
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du total des événements: {str(e)}")
        return {'total_events': 0, 'error': str(e)}

def get_events_per_agent(user, days=None, limit=5):
    """
    Récupère le nombre d'événements par agent (pour les admins uniquement).
    Retourne les agents avec le plus d'événements.
    """
    if not (user.is_superuser or user.is_staff):
        return {'error': 'Accès réservé aux administrateurs'}
    
    try:
        from agenda.models import Event
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        today = timezone.now().date()
        
        query = Event.objects.all()
        if days:
            end_date = today + timedelta(days=days)
            query = query.filter(
                start_date__date__gte=today,
                start_date__date__lte=end_date
            )
        
        # Annoter chaque agent avec le nombre d'événements
        agents = User.objects.filter(
            events__in=query
        ).annotate(
            event_count=Count('events')
        ).order_by('-event_count')[:limit]
        
        result = [
            {
                'agent_name': f"{agent.first_name} {agent.last_name}",
                'event_count': agent.event_count
            }
            for agent in agents
        ]
        
        return {'events_per_agent': result, 'days': days if days else 'tous les temps'}
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des événements par agent: {str(e)}")
        return {'events_per_agent': [], 'error': str(e)}

def format_event_for_display(event):
    """
    Formate un événement pour l'affichage.
    """
    if not event:
        return None
    
    try:
        agents_list = [f"{agent.first_name} {agent.last_name}" for agent in event.agents.all()]
        
        formatted_date = event.start_date.strftime('%d/%m/%Y')
        formatted_time = event.start_date.strftime('%H:%M')
        
        return {
            'id': event.id,
            'title': getattr(event, 'title', 'Événement sans titre'),
            'date': formatted_date,
            'time': formatted_time,
            'location': event.location,
            'description': getattr(event, 'description', 'Aucune description'),
            'agents': agents_list,
            'company_name': event.company_name,
        }
    
    except Exception as e:
        logger.error(f"Erreur lors du formatage de l'événement {event.id}: {str(e)}")
        return {
            'id': event.id,
            'title': getattr(event, 'title', 'Événement'),
            'date': 'Erreur de formatage',
            'error': str(e)
        }

# ===== FONCTIONS POUR LES PRÉSENCES =====

def get_agent_presence_stats(user, agent_id=None, days=30):
    """
    Récupère les statistiques de présence d'un agent.
    Pour un admin, peut accéder aux stats de n'importe quel agent.
    Pour un agent, accès à ses propres stats détaillées.
    """
    if agent_id and not isinstance(agent_id, int):
        logger.warning(f"ID d'agent invalide: {agent_id}")
        return {'error': 'ID d\'agent invalide'}
    
    try:
        from presence.models import Presence
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        if (user.is_superuser or user.is_staff) and agent_id:
            try:
                agent = User.objects.get(id=agent_id)
            except User.DoesNotExist:
                return {
                    'error': f"Agent avec ID {agent_id} non trouvé"
                }
        else:
            agent = user
        
        start_date = timezone.now().date() - timedelta(days=days)
        
        presences = Presence.objects.filter(
            agent=agent,
            timestamp__date__gte=start_date
        ).select_related('agent')
        
        # Ajouter des détails pour l'agent
        locations = {}
        for presence in presences:
            location = presence.location_name or 'Non spécifiée'
            locations[location] = locations.get(location, 0) + 1
        
        stats = {
            'agent_name': f"{agent.first_name} {agent.last_name}",
            'total': presences.count(),
            'approved': presences.filter(status='approved').count(),
            'rejected': presences.filter(status='rejected').count(),
            'pending': presences.filter(status='pending').count(),
            'last_presence': presences.order_by('-timestamp').first(),
            'locations': locations,
            'days_analyzed': days
        }
        
        return stats
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques de présence: {str(e)}")
        return {
            'total': 0,
            'approved': 0,
            'rejected': 0,
            'pending': 0,
            'error': str(e)
        }

def get_total_presences(user, days=None):
    """
    Récupère le nombre total de présences.
    Si days est spécifié, limite aux présences dans cette période.
    """
    try:
        from presence.models import Presence
        
        query = Presence.objects.all().select_related('agent')
        
        if days:
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=days)
            query = query.filter(
                timestamp__date__gte=start_date,
                timestamp__date__lte=end_date
            )
        
        if not (user.is_superuser or user.is_staff):
            query = query.filter(agent=user)
        
        total = query.count()
        return {'total_presences': total, 'days': days if days else 'tous les temps'}
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du total des présences: {str(e)}")
        return {'total_presences': 0, 'error': str(e)}

def get_presences_by_location(user, days=None):
    """
    Récupère les présences par localisation (pour les admins uniquement).
    """
    if not (user.is_superuser or user.is_staff):
        return {'error': 'Accès réservé aux administrateurs'}
    
    try:
        from presence.models import Presence
        
        query = Presence.objects.all().select_related('agent')
        
        if days:
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=days)
            query = query.filter(
                timestamp__date__gte=start_date,
                timestamp__date__lte=end_date
            )
        
        # Grouper par localisation
        locations = {}
        for presence in query:
            location = presence.location_name or 'Non spécifiée'
            locations[location] = locations.get(location, 0) + 1
        
        return {'presences_by_location': locations, 'days': days if days else 'tous les temps'}
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des présences par localisation: {str(e)}")
        return {'presences_by_location': {}, 'error': str(e)}

def format_presence_for_display(presence):
    """
    Formate une présence pour l'affichage.
    """
    if not presence:
        return None
    return {
        'timestamp': presence.timestamp.strftime('%d/%m/%Y %H:%M'),
        'location': presence.location_name or 'Non spécifiée',
        'status': presence.status,
        'agent_name': f"{presence.agent.first_name} {presence.agent.last_name}",
    }

def get_last_presence(user, agent_id=None):
    """
    Récupère la dernière présence enregistrée.
    Pour un admin, peut accéder à la dernière présence de n'importe quel agent.
    """
    if agent_id and not isinstance(agent_id, int):
        logger.warning(f"ID d'agent invalide: {agent_id}")
        return None
    
    try:
        from presence.models import Presence
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        if (user.is_superuser or user.is_staff) and agent_id:
            try:
                agent = User.objects.get(id=agent_id)
            except User.DoesNotExist:
                return None
        else:
            agent = user
        
        last_presence = Presence.objects.filter(
            agent=agent
        ).select_related('agent').order_by('-timestamp').first()
        
        return format_presence_for_display(last_presence)
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la dernière présence: {str(e)}")
        return None

# ===== FONCTIONS POUR LES PAIEMENTS =====

def get_payment_summary(user, agent_id=None, months=3):
    """
    Récupère un résumé des paiements pour un agent.
    Pour un admin, peut accéder aux paiements de n'importe quel agent.
    Pour un agent, accès à ses propres paiements détaillés.
    """
    if agent_id and not isinstance(agent_id, int):
        logger.warning(f"ID d'agent invalide: {agent_id}")
        return {'error': 'ID d\'agent invalide'}
    
    try:
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        if (user.is_superuser or user.is_staff) and agent_id:
            try:
                agent = User.objects.get(id=agent_id)
            except User.DoesNotExist:
                return {
                    'error': f"Agent avec ID {agent_id} non trouvé"
                }
        else:
            agent = user
        
        try:
            from payment.models import Payment
            
            start_date = timezone.now().date() - timedelta(days=30 * months)
            
            payments = Payment.objects.filter(
                agent=agent,
                created_at__date__gte=start_date
            ).select_related('agent').order_by('-created_at')
            
            total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
            last_payment = payments.first()
            
            # Détails des paiements par mois pour l'agent
            monthly_payments = {}
            for payment in payments:
                month = payment.created_at.strftime('%Y-%m')
                monthly_payments[month] = monthly_payments.get(month, 0) + float(payment.amount)
            
            today = timezone.now().date()
            if today.day < 10:
                next_payment_date = datetime(today.year, today.month, 10).date()
            else:
                if today.month == 12:
                    next_payment_date = datetime(today.year + 1, 1, 10).date()
                else:
                    next_payment_date = datetime(today.year, today.month + 1, 10).date()
            
            return {
                'agent_name': f"{agent.first_name} {agent.last_name}",
                'total_amount': total_amount,
                'payment_count': payments.count(),
                'last_payment': {
                    'date': last_payment.created_at.strftime('%d/%m/%Y') if last_payment else 'Aucun',
                    'amount': last_payment.amount if last_payment else 0,
                },
                'monthly_payments': monthly_payments,
                'next_payment_date': next_payment_date.strftime('%d/%m/%Y'),
                'months_analyzed': months
            }
        
        except ImportError:
            logger.warning("Modèle Payment non disponible")
            return {
                'agent_name': f"{agent.first_name} {agent.last_name}",
                'error': 'Modèle de paiement non disponible dans le système',
                'note': 'Contactez l\'administrateur pour plus de détails'
            }
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations de paiement: {str(e)}")
        return {
            'error': 'Impossible de récupérer les informations de paiement',
            'total_amount': 0
        }

def get_total_payments(user, months=None):
    """
    Récupère le montant total des paiements.
    Si months est spécifié, limite aux paiements dans cette période.
    """
    try:
        from payment.models import Payment
        
        query = Payment.objects.all().select_related('agent')
        
        if months:
            start_date = timezone.now().date() - timedelta(days=30 * months)
            query = query.filter(
                created_at__date__gte=start_date
            )
        
        if not (user.is_superuser or user.is_staff):
            query = query.filter(agent=user)
        
        total = query.aggregate(Sum('amount'))['amount__sum'] or 0
        return {'total_payments': total, 'months': months if months else 'tous les temps'}
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du total des paiements: {str(e)}")
        return {'total_payments': 0, 'error': str(e)}

def get_payments_by_period(user, months=None):
    """
    Récupère les paiements par période (par mois) pour les admins.
    """
    if not (user.is_superuser or user.is_staff):
        return {'error': 'Accès réservé aux administrateurs'}
    
    try:
        from payment.models import Payment
        
        query = Payment.objects.all().select_related('agent')
        
        if months:
            start_date = timezone.now().date() - timedelta(days=30 * months)
            query = query.filter(
                created_at__date__gte=start_date
            )
        
        # Grouper par mois
        monthly_payments = {}
        for payment in query:
            month = payment.created_at.strftime('%Y-%m')
            monthly_payments[month] = monthly_payments.get(month, 0) + float(payment.amount)
        
        return {'payments_by_period': monthly_payments, 'months': months if months else 'tous les temps'}
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des paiements par période: {str(e)}")
        return {'payments_by_period': {}, 'error': str(e)}

# ===== FONCTIONS POUR LES AGENTS =====

def get_total_agents(user):
    """
    Récupère le nombre total d'agents dans le système.
    Accessible uniquement aux admins.
    """
    if not (user.is_superuser or user.is_staff):
        return {'error': 'Accès réservé aux administrateurs'}
    
    try:
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        total = User.objects.count()
        return {'total_agents': total}
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du total des agents: {str(e)}")
        return {'total_agents': 0, 'error': str(e)}

def get_all_agents(user, limit=10):
    """
    Liste tous les agents avec des informations de base (pour les admins uniquement).
    """
    if not (user.is_superuser or user.is_staff):
        return {'error': 'Accès réservé aux administrateurs'}
    
    try:
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        agents = User.objects.all()[:limit]
        
        result = [
            {
                'id': agent.id,
                'name': f"{agent.first_name} {agent.last_name}",
                'username': agent.username,
                'email': agent.email or 'Non spécifié',
                'is_admin': agent.is_superuser or agent.is_staff
            }
            for agent in agents
        ]
        
        return {'agents': result, 'total': User.objects.count()}
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des agents: {str(e)}")
        return {'agents': [], 'error': str(e)}

# ===== FONCTIONS POUR LE PROFIL ET LES PRÉFÉRENCES =====

def get_agent_profile_data(user, agent_id=None):
    """
    Récupère les données complètes du profil d'un agent.
    Pour un admin, peut accéder au profil de n'importe quel agent.
    Pour un agent, accès complet à son propre profil.
    """
    if agent_id and not isinstance(agent_id, int):
        logger.warning(f"ID d'agent invalide: {agent_id}")
        return {'error': 'ID d\'agent invalide'}
    
    try:
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        if (user.is_superuser or user.is_staff) and agent_id:
            try:
                agent = User.objects.get(id=agent_id)
            except User.DoesNotExist:
                return {
                    'error': f"Agent avec ID {agent_id} non trouvé"
                }
        else:
            agent = user
        
        photo_count = 0
        try:
            photo_count = agent.presences.count()
        except:
            pass
        
        joined_date = agent.date_joined.strftime('%d/%m/%Y') if hasattr(agent, 'date_joined') else 'Inconnue'
        event_stats = get_agent_event_stats(agent)
        presence_stats = get_agent_presence_stats(user, agent.id if (user.is_superuser or user.is_staff) else None)
        payment_summary = get_payment_summary(user, agent.id if (user.is_superuser or user.is_staff) else None)
        
        # Récupérer les disponibilités et préférences
        availabilities = []
        preferences = {}
        try:
            from accounts.models import AgentAvailability, AgentPreference
            availabilities = AgentAvailability.objects.filter(agent=agent).order_by('date')[:5]
            preferences_obj = AgentPreference.objects.filter(agent=agent).first()
            if preferences_obj:
                preferences = {
                    'preferred_locations': preferences_obj.preferred_locations or 'Non spécifié',
                    'preferred_event_types': preferences_obj.preferred_event_types or 'Non spécifié',
                    'max_events_per_week': preferences_obj.max_events_per_week,
                    'max_events_per_month': preferences_obj.max_events_per_month,
                }
        except ImportError:
            logger.warning("Modèles AgentAvailability ou AgentPreference non disponibles")
        
        return {
            'username': agent.username,
            'full_name': f"{agent.first_name} {agent.last_name}".strip() or 'Non spécifié',
            'email': agent.email or 'Non spécifié',
            'age': getattr(agent, 'age', 'Non spécifié'),
            'gender': getattr(agent, 'gender', 'Non spécifié'),
            'location': getattr(agent, 'location', 'Non spécifiée'),
            'phone': getattr(agent, 'phone_number', 'Non spécifié'),
            'measurements': getattr(agent, 'measurements', 'Non spécifiées'),
            'joined_date': joined_date,
            'photo_count': photo_count,
            'total_payments': getattr(agent, 'total_payments', 0),
            'event_stats': event_stats,
            'presence_stats': presence_stats,
            'payment_summary': payment_summary,
            'availabilities': [
                {
                    'date': availability.date.strftime('%d/%m/%Y'),
                    'is_available': availability.is_available,
                    'note': availability.note or 'Aucune note'
                }
                for availability in availabilities
            ],
            'preferences': preferences,
            'is_admin': agent.is_superuser or agent.is_staff
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données de profil: {str(e)}")
        return {
            'username': getattr(user, 'username', 'Inconnu'),
            'error': 'Impossible de récupérer toutes les informations du profil'
        }

def get_agent_event_stats(user, agent_id=None):
    """
    Récupère les statistiques d'événements pour un agent.
    Pour un admin, peut accéder aux stats de n'importe quel agent.
    """
    try:
        from agenda.models import Event
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        if (user.is_superuser or user.is_staff) and agent_id:
            try:
                agent = User.objects.get(id=agent_id)
            except User.DoesNotExist:
                return {
                    'error': f"Agent avec ID {agent_id} non trouvé"
                }
        else:
            agent = user
        
        today = timezone.now().date()
        
        events = Event.objects.filter(
            Q(agents=agent)
        ).annotate(
            is_past=Case(
                When(start_date__date__lt=today, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        )
        
        past_count = events.filter(is_past=1).count()
        future_count = events.filter(is_past=0).count()
        
        # Ajouter des détails par localisation pour l'agent
        locations = {}
        for event in events:
            location = event.location or 'Non spécifiée'
            locations[location] = locations.get(location, 0) + 1
        
        return {
            'past_events': past_count,
            'future_events': future_count,
            'total_events': past_count + future_count,
            'locations': locations
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques d'événements: {str(e)}")
        return {
            'past_events': 0,
            'future_events': 0,
            'total_events': 0,
            'error': str(e)
        }

# ===== FONCTIONS D'AIDE POUR LE CHATBOT =====

def extract_date_range(message):
    """
    Extrait une plage de dates à partir d'un message.
    """
    import re
    from dateutil.relativedelta import relativedelta
    
    message = message.lower()
    today = timezone.now().date()
    
    if "aujourd'hui" in message or "aujourd hui" in message:
        return today, today
    
    if "demain" in message:
        tomorrow = today + timedelta(days=1)
        return tomorrow, tomorrow
    
    if "cette semaine" in message:
        days_until_sunday = 6 - today.weekday()
        end_of_week = today + timedelta(days=days_until_sunday)
        return today, end_of_week
    
    if "semaine prochaine" in message:
        days_until_monday = 7 - today.weekday()
        next_monday = today + timedelta(days=days_until_monday)
        next_sunday = next_monday + timedelta(days=6)
        return next_monday, next_sunday
    
    if "ce mois" in message or "ce mois-ci" in message:
        last_day = (today.replace(day=1) + relativedelta(months=1) - timedelta(days=1)).day
        end_of_month = today.replace(day=last_day)
        return today, end_of_month
    
    if "mois prochain" in message:
        first_of_next_month = today.replace(day=1) + relativedelta(months=1)
        last_of_next_month = (first_of_next_month + relativedelta(months=1) - timedelta(days=1))
        return first_of_next_month, last_of_next_month
    
    range_pattern = r'du (\d{1,2})[/.-](\d{1,2})(?:[/.-](\d{2,4}))? au (\d{1,2})[/.-](\d{1,2})(?:[/.-](\d{2,4}))?'
    match = re.search(range_pattern, message)
    if match:
        start_day, start_month, start_year, end_day, end_month, end_year = match.groups()
        start_year = int(start_year) if start_year else today.year
        end_year = int(end_year) if end_year else today.year
        if start_year < 100:
            start_year += 2000
        if end_year < 100:
            end_year += 2000
        try:
            start_date = datetime(int(start_year), int(start_month), int(start_day)).date()
            end_date = datetime(int(end_year), int(end_month), int(end_day)).date()
            return start_date, end_date
        except ValueError:
            pass
    
    date_pattern = r'(\d{1,2})[/.-](\d{1,2})(?:[/.-](\d{2,4}))?'
    matches = re.findall(date_pattern, message)
    
    if matches:
        try:
            day, month, year = matches[0]
            day = int(day)
            month = int(month)
            
            if year:
                year = int(year)
                if year < 100:
                    year = 2000 + year
            else:
                year = today.year
            
            if 1 <= day <= 31 and 1 <= month <= 12:
                specific_date = datetime(year, month, day).date()
                return specific_date, specific_date
        except ValueError:
            pass
    
    return None, None

def extract_location(message):
    """
    Extrait un emplacement à partir d'un message.
    """
    import re
    
    message = message.lower()
    
    location_patterns = [
        r'à ([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'au ([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'en ([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'dans ([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'près de ([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'lieu[:\s]+([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'emplacement[:\s]+([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'localisation[:\s]+([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'à ([a-zéèêëàâäôöùûüÿçœæ\s-]+) \d{1,2}(?:er?|ème)?'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, message)
        if match:
            location = match.group(1).strip()
            stop_words = ['le', 'la', 'les', 'du', 'de', 'des', 'l', 'un', 'une']
            for word in stop_words:
                if location.startswith(word + ' '):
                    location = location[len(word)+1:]
            
            return location
    
    return None

def extract_agent_id(message):
    """
    Extrait l'ID d'un agent à partir d'un message.
    """
    import re
    
    agent_id_patterns = [
        r'agent\s+(\d+)',
        r'agent\s+id\s+(\d+)',
        r'agent\s+#(\d+)',
        r'agent\s+numéro\s+(\d+)',
        r'agent\s+numero\s+(\d+)',
        r'id\s+(\d+)',
        r'#(\d+)'
    ]
    
    for pattern in agent_id_patterns:
        match = re.search(pattern, message.lower())
        if match:
            return int(match.group(1))
    
    return None

def format_data_for_prompt(data, data_type):
    """
    Formate les données pour le prompt du chatbot.
    """
    if not data:
        return "Aucune donnée disponible."
    
    if data_type == 'events':
        if isinstance(data, list) and len(data) == 0:
            return "Aucun événement trouvé."
        
        if hasattr(data, '__iter__') and not isinstance(data, dict):
            result = "===== Liste des événements =====\n"
            for event in data:
                event_info = format_event_for_display(event)
                result += f"- {event_info['title']} (ID: {event_info['id']})\n"
                result += f"  Date: {event_info['date']} à {event_info['time']}\n"
                result += f"  Lieu: {event_info['location']}\n"
                result += f"  {event_info.get('description', 'Aucune description')[:100]}{'...' if len(event_info.get('description', '')) > 100 else ''}\n\n"
            return result
        else:
            event_info = format_event_for_display(data)
            result = "===== Détails de l'événement =====\n"
            result += f"Événement: {event_info['title']} (ID: {event_info['id']})\n"
            result += f"Date: {event_info['date']} à {event_info['time']}\n"
            result += f"Lieu: {event_info['location']}\n"
            result += f"Description: {event_info.get('description', 'Aucune description')}\n"
            if 'error' in event_info:
                result += f"Erreur: {event_info['error']}\n"
            return result
    
    elif data_type == 'profile':
        result = f"===== Profil de l'agent =====\n" \
                 f"Nom: {data['full_name']}\n" \
                 f"Email: {data['email']}\n" \
                 f"Téléphone: {data['phone']}\n" \
                 f"Localisation: {data['location']}\n" \
                 f"Âge: {data['age']}\n" \
                 f"Genre: {data['gender']}\n" \
                 f"Inscrit depuis: {data['joined_date']}\n" \
                 f"Événements passés: {data['event_stats']['past_events']}\n" \
                 f"Événements à venir: {data['event_stats']['future_events']}\n" \
                 f"Présences totales: {data['presence_stats']['total']}\n" \
                 f"Présences approuvées: {data['presence_stats']['approved']}\n" \
                 f"Paiements totaux: {data['payment_summary']['total_amount']} ARIARY\n"
        
        # Ajouter les disponibilités
        result += "===== Disponibilités =====\n"
        if data['availabilities']:
            for availability in data['availabilities']:
                result += f"- {availability['date']}: {'Disponible' if availability['is_available'] else 'Non disponible'} ({availability['note']})\n"
        else:
            result += "Aucune disponibilité enregistrée.\n"
        
        # Ajouter les préférences
        result += "===== Préférences =====\n"
        if data['preferences']:
            result += f"Emplacements préférés: {data['preferences']['preferred_locations']}\n"
            result += f"Types d'événements préférés: {data['preferences']['preferred_event_types']}\n"
            result += f"Max événements par semaine: {data['preferences']['max_events_per_week']}\n"
            result += f"Max événements par mois: {data['preferences']['max_events_per_month']}\n"
        else:
            result += "Aucune préférence enregistrée.\n"
        
        return result
    
    elif data_type == 'presence_stats':
        result = f"===== Statistiques de présence pour {data.get('agent_name', 'l\'agent')} =====\n" \
                 f"Total des présences: {data['total']}\n" \
                 f"Approuvées: {data['approved']}\n" \
                 f"En attente: {data['pending']}\n" \
                 f"Rejetées: {data['rejected']}\n" \
                 f"Période analysée: {data['days_analyzed']} jours\n"
        result += "===== Présences par localisation =====\n"
        for location, count in data['locations'].items():
            result += f"- {location}: {count}\n"
        return result
    
    elif data_type == 'payment':
        if 'error' in data:
            return f"===== Informations de paiement =====\n" \
                   f"Erreur: {data['error']}\n" \
                   f"Note: {data.get('note', 'Contactez l\'administrateur pour plus de détails')}"
        result = f"===== Informations de paiement pour {data.get('agent_name', 'l\'agent')} =====\n" \
                 f"Total des paiements: {data.get('total_amount', 0)} ARIARY\n" \
                 f"Dernier paiement: {data.get('last_payment', {}).get('amount', 0)} ARIARY le {data.get('last_payment', {}).get('date', 'N/A')}\n" \
                 f"Prochain paiement prévu: {data.get('next_payment_date', 'le 10 du mois prochain')}\n"
        result += "===== Paiements par mois =====\n"
        for month, amount in data['monthly_payments'].items():
            result += f"- {month}: {amount} ARIARY\n"
        return result
    
    elif data_type == 'total_events':
        if 'error' in data:
            return f"===== Statistiques globales =====\nErreur: {data['error']}"
        return f"===== Statistiques globales =====\nNombre total d'événements: {data['total_events']}\nPériode: {data['days']}"
    
    elif data_type == 'total_presences':
        if 'error' in data:
            return f"===== Statistiques globales =====\nErreur: {data['error']}"
        return f"===== Statistiques globales =====\nNombre total de présences: {data['total_presences']}\nPériode: {data['days']}"
    
    elif data_type == 'total_payments':
        if 'error' in data:
            return f"===== Statistiques globales =====\nErreur: {data['error']}"
        return f"===== Statistiques globales =====\nMontant total des paiements: {data['total_payments']} ARIARY\nPériode: {data['months']}"
    
    elif data_type == 'total_agents':
        if 'error' in data:
            return f"===== Statistiques globales =====\nErreur: {data['error']}"
        return f"===== Statistiques globales =====\nNombre total d'agents: {data['total_agents']}"
    
    elif data_type == 'events_per_agent':
        if 'error' in data:
            return f"===== Statistiques globales =====\nErreur: {data['error']}"
        result = f"===== Événements par agent (Top {len(data['events_per_agent'])}) =====\n"
        for entry in data['events_per_agent']:
            result += f"- {entry['agent_name']}: {entry['event_count']} événements\n"
        result += f"Période: {data['days']}"
        return result
    
    elif data_type == 'presences_by_location':
        if 'error' in data:
            return f"===== Statistiques globales =====\nErreur: {data['error']}"
        result = f"===== Présences par localisation =====\n"
        for location, count in data['presences_by_location'].items():
            result += f"- {location}: {count} présences\n"
        result += f"Période: {data['days']}"
        return result
    
    elif data_type == 'payments_by_period':
        if 'error' in data:
            return f"===== Statistiques globales =====\nErreur: {data['error']}"
        result = f"===== Paiements par période =====\n"
        for month, amount in data['payments_by_period'].items():
            result += f"- {month}: {amount} ARIARY\n"
        result += f"Période: {data['months']}"
        return result
    
    elif data_type == 'all_agents':
        if 'error' in data:
            return f"===== Liste des agents =====\nErreur: {data['error']}"
        result = f"===== Liste des agents (Top {len(data['agents'])}) =====\n"
        for agent in data['agents']:
            result += f"- {agent['name']} (ID: {agent['id']}, {agent['username']})\n"
            result += f"  Email: {agent['email']}\n"
            result += f"  Admin: {'Oui' if agent['is_admin'] else 'Non'}\n"
        result += f"Total d'agents: {data['total']}"
        return result
    
    return str(data)