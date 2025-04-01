"""
Utilitaires pour le chatbot - Fonctions de récupération et formatage des données
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Sum, Count, Avg
from django.core.exceptions import ObjectDoesNotExist

# Configurez le logger pour ce module
logger = logging.getLogger(__name__)

# ===== FONCTIONS POUR LES ÉVÉNEMENTS =====

def get_upcoming_events(user, days=7, limit=5):
    """
    Récupère les événements à venir pour un utilisateur.
    """
    try:
        from agenda.models import Event  # Import local pour éviter les imports circulaires
        
        today = timezone.now().date()
        end_date = today + timedelta(days=days)
        
        # Si admin, récupérer tous les événements
        if user.is_superuser or user.is_staff:
            upcoming_events = Event.objects.filter(
                date__gte=today,
                date__lte=end_date
            ).order_by('date')[:limit]
        else:
            # Pour un agent, seulement ses événements
            upcoming_events = Event.objects.filter(
                Q(agents=user) | Q(assigned_to=user),
                date__gte=today,
                date__lte=end_date
            ).order_by('date')[:limit]
        
        return upcoming_events
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des événements: {str(e)}")
        return []

def get_event_details(event_id, user):
    """
    Récupère les détails d'un événement spécifique.
    """
    try:
        from agenda.models import Event
        
        # Si admin, accès à tous les événements
        if user.is_superuser or user.is_staff:
            event = Event.objects.get(id=event_id)
        else:
            # Pour un agent, vérifier l'autorisation
            event = Event.objects.filter(
                id=event_id
            ).filter(
                Q(agents=user) | Q(assigned_to=user)
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
        
        # Recherche avec icontains pour une correspondance partielle
        if user.is_superuser or user.is_staff:
            events = Event.objects.filter(
                location__icontains=location,
                date__gte=today,
                date__lte=end_date
            ).order_by('date')[:limit]
        else:
            events = Event.objects.filter(
                Q(agents=user) | Q(assigned_to=user),
                location__icontains=location,
                date__gte=today,
                date__lte=end_date
            ).order_by('date')[:limit]
        
        return events
    
    except Exception as e:
        logger.error(f"Erreur lors de la recherche d'événements par emplacement: {str(e)}")
        return []

def get_next_event(user):
    """
    Récupère le prochain événement de l'utilisateur.
    """
    try:
        from agenda.models import Event
        
        today = timezone.now().date()
        
        if user.is_superuser or user.is_staff:
            next_event = Event.objects.filter(
                date__gte=today
            ).order_by('date', 'time').first()
        else:
            next_event = Event.objects.filter(
                Q(agents=user) | Q(assigned_to=user),
                date__gte=today
            ).order_by('date', 'time').first()
        
        return next_event
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du prochain événement: {str(e)}")
        return None

def format_event_for_display(event):
    """
    Formate un événement pour l'affichage.
    """
    if not event:
        return None
    
    try:
        # Récupérer les agents assignés
        agents_list = []
        if hasattr(event, 'agents') and event.agents.exists():
            agents_list = [f"{agent.first_name} {agent.last_name}" for agent in event.agents.all()]
        
        # Formater la date et l'heure
        formatted_date = event.date.strftime('%d/%m/%Y') if hasattr(event, 'date') else 'Non spécifiée'
        formatted_time = event.time.strftime('%H:%M') if hasattr(event, 'time') and event.time else 'Non spécifiée'
        
        return {
            'id': event.id,
            'title': event.title,
            'date': formatted_date,
            'time': formatted_time,
            'location': event.location if hasattr(event, 'location') else 'Non spécifié',
            'description': event.description if hasattr(event, 'description') else 'Aucune description',
            'agents': agents_list,
            'status': event.status if hasattr(event, 'status') else 'Non spécifié',
            'client': event.client.name if hasattr(event, 'client') and event.client else 'Non spécifié'
        }
    
    except Exception as e:
        logger.error(f"Erreur lors du formatage de l'événement {event.id}: {str(e)}")
        # Retourner un format minimal en cas d'erreur
        return {
            'id': event.id if hasattr(event, 'id') else 'Inconnu',
            'title': event.title if hasattr(event, 'title') else 'Événement',
            'date': 'Erreur de formatage',
            'error': 'Impossible de récupérer tous les détails'
        }

# ===== FONCTIONS POUR LES PRÉSENCES =====

def get_agent_presence_stats(user, agent_id=None):
    """
    Récupère les statistiques de présence d'un agent.
    """
    try:
        from presence.models import Presence
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Si admin et agent_id fourni, récupérer les stats de cet agent
        if (user.is_superuser or user.is_staff) and agent_id:
            try:
                agent = User.objects.get(id=agent_id)
            except User.DoesNotExist:
                return {
                    'error': f"Agent avec ID {agent_id} non trouvé"
                }
        else:
            # Sinon, utiliser l'utilisateur actuel
            agent = user
        
        start_date = timezone.now().date() - timedelta(days=30)
        
        presences = Presence.objects.filter(
            agent=agent,
            timestamp__date__gte=start_date
        )
        
        stats = {
            'agent_name': f"{agent.first_name} {agent.last_name}",
            'total': presences.count(),
            'approved': presences.filter(status='approved').count(),
            'rejected': presences.filter(status='rejected').count(),
            'pending': presences.filter(status='pending').count(),
            'last_presence': presences.order_by('-timestamp').first(),
            'days_analyzed': 30
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

def get_last_presence(user, agent_id=None):
    """
    Récupère la dernière présence enregistrée par l'agent.
    """
    try:
        from presence.models import Presence
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Si admin et agent_id fourni
        if (user.is_superuser or user.is_staff) and agent_id:
            try:
                agent = User.objects.get(id=agent_id)
            except User.DoesNotExist:
                return None
        else:
            agent = user
        
        last_presence = Presence.objects.filter(
            agent=agent
        ).order_by('-timestamp').first()
        
        return last_presence
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la dernière présence: {str(e)}")
        return None

# ===== FONCTIONS POUR LES PAIEMENTS =====

def get_payment_summary(user, agent_id=None):
    """
    Récupère un résumé des paiements pour un agent.
    """
    try:
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Si admin et agent_id fourni
        if (user.is_superuser or user.is_staff) and agent_id:
            try:
                agent = User.objects.get(id=agent_id)
            except User.DoesNotExist:
                return {
                    'error': f"Agent avec ID {agent_id} non trouvé"
                }
        else:
            agent = user
        
        # Adapter selon votre modèle de paiement
        try:
            from payments.models import Payment # type: ignore
            
            start_date = timezone.now().date() - timedelta(days=90)  # 3 mois
            
            payments = Payment.objects.filter(
                agent=agent,
                date__gte=start_date
            ).order_by('-date')
            
            total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
            
            # Récupérer le dernier paiement
            last_payment = payments.first()
            
            # Calculer le prochain paiement (exemple: le 10 du mois prochain)
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
                    'date': last_payment.date.strftime('%d/%m/%Y') if last_payment else 'Aucun',
                    'amount': last_payment.amount if last_payment else 0,
                    'status': last_payment.status if last_payment and hasattr(last_payment, 'status') else 'N/A'
                },
                'next_payment_date': next_payment_date.strftime('%d/%m/%Y'),
                'months_analyzed': 3
            }
        
        except ImportError:
            # Si le modèle Payment n'existe pas, utiliser les données de l'agent
            return {
                'agent_name': f"{agent.first_name} {agent.last_name}",
                'total_payments': agent.total_payments if hasattr(agent, 'total_payments') else 0,
                'next_payment_date': 'Le 10 du mois prochain',
                'note': 'Informations limitées - contactez l\'administrateur pour plus de détails'
            }
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations de paiement: {str(e)}")
        return {
            'error': 'Impossible de récupérer les informations de paiement',
            'total_payments': 0
        }

# ===== FONCTIONS POUR LE PROFIL =====

def get_agent_profile_data(user, agent_id=None):
    """
    Récupère les données complètes du profil d'un agent.
    """
    try:
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Si admin et agent_id fourni
        if (user.is_superuser or user.is_staff) and agent_id:
            try:
                agent = User.objects.get(id=agent_id)
            except User.DoesNotExist:
                return {
                    'error': f"Agent avec ID {agent_id} non trouvé"
                }
        else:
            agent = user
        
        # Récupérer les photos si disponibles
        photo_count = 0
        try:
            photo_count = agent.photos.count() if hasattr(agent, 'photos') else 0
        except:
            pass
        
        # Formater la date d'inscription
        joined_date = agent.date_joined.strftime('%d/%m/%Y') if hasattr(agent, 'date_joined') else 'Inconnue'
        
        # Récupérer les statistiques d'événements
        event_stats = get_agent_event_stats(agent)
        
        return {
            'username': agent.username,
            'full_name': f"{agent.first_name} {agent.last_name}".strip() or 'Non spécifié',
            'email': agent.email or 'Non spécifié',
            'age': agent.age if hasattr(agent, 'age') else 'Non spécifié',
            'gender': agent.gender if hasattr(agent, 'gender') else 'Non spécifié',
            'location': agent.location if hasattr(agent, 'location') else 'Non spécifiée',
            'phone': agent.phone_number if hasattr(agent, 'phone_number') else 'Non spécifié',
            'measurements': agent.measurements if hasattr(agent, 'measurements') else 'Non spécifiées',
            'joined_date': joined_date,
            'photo_count': photo_count,
            'total_payments': agent.total_payments if hasattr(agent, 'total_payments') else 0,
            'event_stats': event_stats,
            'is_admin': agent.is_superuser or agent.is_staff
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données de profil: {str(e)}")
        return {
            'username': getattr(user, 'username', 'Inconnu'),
            'error': 'Impossible de récupérer toutes les informations du profil'
        }

def get_agent_event_stats(user):
    """
    Récupère les statistiques d'événements pour un agent.
    """
    try:
        from agenda.models import Event
        
        # Événements passés
        past_events = Event.objects.filter(
            Q(agents=user) | Q(assigned_to=user),
            date__lt=timezone.now().date()
        )
        
        # Événements à venir
        future_events = Event.objects.filter(
            Q(agents=user) | Q(assigned_to=user),
            date__gte=timezone.now().date()
        )
        
        return {
            'past_events': past_events.count(),
            'future_events': future_events.count(),
            'total_events': past_events.count() + future_events.count()
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques d'événements: {str(e)}")
        return {
            'past_events': 0,
            'future_events': 0,
            'total_events': 0
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
    
    # Rechercher des périodes spécifiques
    if "aujourd'hui" in message or "aujourd hui" in message:
        return today, today
    
    if "demain" in message:
        tomorrow = today + timedelta(days=1)
        return tomorrow, tomorrow
    
    if "cette semaine" in message:
        # Du jour actuel à la fin de la semaine (dimanche)
        days_until_sunday = 6 - today.weekday()
        end_of_week = today + timedelta(days=days_until_sunday)
        return today, end_of_week
    
    if "semaine prochaine" in message:
        # Lundi prochain à dimanche prochain
        days_until_monday = 7 - today.weekday()
        next_monday = today + timedelta(days=days_until_monday)
        next_sunday = next_monday + timedelta(days=6)
        return next_monday, next_sunday
    
    if "ce mois" in message or "ce mois-ci" in message:
        # Du jour actuel à la fin du mois
        last_day = (today.replace(day=1) + relativedelta(months=1) - timedelta(days=1)).day
        end_of_month = today.replace(day=last_day)
        return today, end_of_month
    
    if "mois prochain" in message:
        # Du 1er au dernier jour du mois prochain
        first_of_next_month = today.replace(day=1) + relativedelta(months=1)
        last_of_next_month = (first_of_next_month + relativedelta(months=1) - timedelta(days=1))
        return first_of_next_month, last_of_next_month
    
    # Rechercher des dates spécifiques (format JJ/MM ou JJ/MM/AAAA)
    date_pattern = r'(\d{1,2})[/.-](\d{1,2})(?:[/.-](\d{2,4}))?'
    matches = re.findall(date_pattern, message)
    
    if matches:
        try:
            day, month, year = matches[0]
            day = int(day)
            month = int(month)
            
            if year:
                year = int(year)
                # Gérer les années à 2 chiffres
                if year < 100:
                    year = 2000 + year
            else:
                year = today.year
            
            # Valider la date
            if 1 <= day <= 31 and 1 <= month <= 12:
                specific_date = datetime(year, month, day).date()
                return specific_date, specific_date
        except ValueError:
            pass
    
    # Si aucune correspondance n'est trouvée
    return None, None

def extract_location(message):
    """
    Extrait un emplacement à partir d'un message.
    """
    import re
    
    message = message.lower()
    
    # Rechercher des patterns comme "à Paris", "au Havre", "en Bretagne"
    location_patterns = [
        r'à ([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'au ([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'en ([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'dans ([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'près de ([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'lieu[:\s]+([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'emplacement[:\s]+([a-zéèêëàâäôöùûüÿçœæ\s-]+)',
        r'localisation[:\s]+([a-zéèêëàâäôöùûüÿçœæ\s-]+)'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, message)
        if match:
            location = match.group(1).strip()
            # Nettoyer la location (enlever les mots parasites)
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
    
    # Rechercher des patterns comme "agent 123", "agent id 123", "agent #123"
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
        return ""
    
    if data_type == 'events':
        if isinstance(data, list) and len(data) == 0:
            return "Aucun événement trouvé."
        
        if hasattr(data, '__iter__') and not isinstance(data, dict):
            # Liste d'événements
            result = "Événements:\n"
            for event in data:
                event_info = format_event_for_display(event)
                result += f"- {event_info['title']} (ID: {event_info['id']})\n"
                result += f"  Date: {event_info['date']} à {event_info['time']}\n"
                result += f"  Lieu: {event_info['location']}\n"
                result += f"  {event_info['description'][:100]}{'...' if len(event_info['description']) > 100 else ''}\n\n"
            return result
        else:
            # Un seul événement
            event_info = format_event_for_display(data)
            return f"Événement: {event_info['title']} (ID: {event_info['id']})\n"
            f"Date: {event_info['date']} à {event_info['time']}\n"
            f"Lieu: {event_info['location']}\n"
            f"Description: {event_info['description']}"
    
    elif data_type == 'profile':
        return f"Profil de l'agent:\n"
        f"Nom: {data['full_name']}\n"
        f"Email: {data['email']}\n"
        f"Téléphone: {data['phone']}\n"
        f"Localisation: {data['location']}\n"
        f"Âge: {data['age']}\n"
        f"Genre: {data['gender']}\n"
        f"Inscrit depuis: {data['joined_date']}\n"
        f"Événements passés: {data['event_stats']['past_events']}\n"
        f"Événements à venir: {data['event_stats']['future_events']}"
    
    elif data_type == 'presence_stats':
        return f"Statistiques de présence pour {data.get('agent_name', 'l\'agent')}:\n"
        f"Total des présences: {data['total']}\n"
        f"Approuvées: {data['approved']}\n"
        f"En attente: {data['pending']}\n"
        f"Rejetées: {data['rejected']}\n"
        f"Période analysée: {data['days_analyzed']} jours"
    
    elif data_type == 'payment':
        if 'error' in data:
            return f"Informations de paiement:\n"
            f"Total des paiements: {data.get('total_payments', 0)} €\n"
            f"Prochain paiement prévu: le 10 du mois prochain"
        else:
            return f"Informations de paiement pour {data.get('agent_name', 'l\'agent')}:\n"
            f"Total des paiements: {data.get('total_amount', 0)} €\n"
            f"Dernier paiement: {data.get('last_payment', {}).get('amount', 0)} € le {data.get('last_payment', {}).get('date', 'N/A')}\n"
            f"Prochain paiement prévu: {data.get('next_payment_date', 'le 10 du mois prochain')}"
    
    # Format par défaut pour les autres types de données
    return str(data)