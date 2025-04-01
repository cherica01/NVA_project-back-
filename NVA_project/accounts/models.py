from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


def validate_image(image):
    # Vérifier si l'image est None
    if not image:
        return
        
    # Vérifier la taille du fichier - limiter à 5MB
    # Pour un BytesIO, utilisez len() au lieu de .size
    if hasattr(image.file, 'size'):
        file_size = image.file.size
    else:
        file_size = len(image.file.getvalue())
        
    limit_mb = 5
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError(f"La taille maximale de l'image est de {limit_mb}MB")


class Agent(AbstractUser):
    """
    Modèle personnalisé pour les utilisateurs de type 'Agent'.
    """
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, null=True, blank=True)
    location = models.CharField(max_length=250, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    measurements = models.TextField(null=True, blank=True)
    total_payments = models.FloatField(default=0.0)

    def __str__(self):
        return self.username

    def photo_count(self):
        """
        Retourne le nombre de photos associées à cet agent.
        """
        return self.photos.count()


class Photo(models.Model):
    PHOTO_TYPES = (
        ('profile', 'Photo de profil'),
        ('cover', 'Photo de couverture'),
        ('animation', 'Photo d\'animation'),
    )
    
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='agent_photos/', validators=[validate_image])
    photo_type = models.CharField(max_length=20, choices=PHOTO_TYPES, default='profile')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_photo_type_display()} de {self.agent.username} ({self.id})"
    
    def save(self, *args, **kwargs):
        # Vérifier s'il existe déjà une photo du même type pour cet agent
        if not self.pk:  # Seulement pour les nouvelles photos
            existing_photo = Photo.objects.filter(agent=self.agent, photo_type=self.photo_type).first()
            if existing_photo:
                # Supprimer l'ancienne photo du même type
                existing_photo.delete()
        super().save(*args, **kwargs)
