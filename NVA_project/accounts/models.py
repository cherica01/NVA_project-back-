from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


def validate_image(image):
    """
    Valide la taille maximale d'une image.
    Limite fixée à 5 Mo pour cet exemple.
    """
    file_size = image.file.size
    limit_mb = 5  # Limite en mégaoctets
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError(f"La taille maximale d'une image est de {limit_mb} Mo.")


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
    """
    Modèle pour gérer les photos associées à un agent.
    """
    agent = models.ForeignKey(
        Agent,
        related_name='photos',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to='photos/',
        validators=[validate_image]  # Valide la taille des images
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.agent.username}"
