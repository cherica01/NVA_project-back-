"""
Détecteur d'intention pour le chatbot
"""

def detect_intent(message, is_admin=False):
    """
    Détecte l'intention de l'utilisateur à partir de son message.
    """
    message = message.lower()
    
    # Définir les intentions et leurs mots-clés associés
    intents = {
        'events': {
            'keywords': [
                'événement', 'evenement', 'agenda', 'planning', 'semaine', 'programme',
                'rendez-vous', 'rdv', 'mission', 'travail', 'quand', 'où', 'ou',
                'prochain', 'suivant', 'date', 'heure', 'lieu'
            ],
            'score': 0
        },
        'profile': {
            'keywords': [
                'profil', 'information', 'détail', 'detail', 'mes données', 'mon compte',
                'mes infos', 'qui suis-je', 'mon profil', 'mes informations', 'personnel'
            ],
            'score': 0
        },
        'payments': {
            'keywords': [
                'paiement', 'salaire', 'rémunération', 'remuneration', 'argent', 'combien',
                'gagné', 'gagne', 'euros', 'montant', 'versement', 'virement', 'banque'
            ],
            'score': 0
        },
        'presence': {
            'keywords': [
                'présence', 'presence', 'pointage', 'enregistrer', 'localisation',
                'géolocalisation', 'position', 'où suis-je', 'dernière présence',
                'statistiques', 'stats', 'approuvé', 'validé', 'rejeté'
            ],
            'score': 0
        },
        'help': {
            'keywords': [
                'aide', 'help', 'comment', 'assistance', 'guide', 'besoin d\'aide',
                'sos', 'instructions', 'tutoriel', 'expliquer', 'explique'
            ],
            'score': 0
        }
    }
    
    # Ajouter des intentions spécifiques pour les administrateurs
    if is_admin:
        intents['agents'] = {
            'keywords': [
                'agent', 'agents', 'liste', 'tous les agents', 'équipe', 'equipe',
                'personnel', 'employés', 'employes', 'membres'
            ],
            'score': 0
        }
        
        intents['stats'] = {
            'keywords': [
                'statistiques', 'stats', 'performance', 'analyse', 'rapport',
                'résumé', 'resume', 'vue d\'ensemble', 'global', 'général', 'general'
            ],
            'score': 0
        }
    
    # Calculer le score pour chaque intention
    for intent, data in intents.items():
        for keyword in data['keywords']:
            if keyword in message:
                # Augmenter le score en fonction de la position du mot-clé
                # Les mots-clés au début du message ont plus de poids
                position_factor = 1.0
                if message.find(keyword) < len(message) / 3:
                    position_factor = 1.5
                
                data['score'] += 1 * position_factor
    
    # Trouver l'intention avec le score le plus élevé
    max_score = 0
    detected_intent = 'general'
    
    for intent, data in intents.items():
        if data['score'] > max_score:
            max_score = data['score']
            detected_intent = intent
    
    # Si le score est trop faible, considérer comme une intention générale
    if max_score < 0.5:
        detected_intent = 'general'
    
    return detected_intent