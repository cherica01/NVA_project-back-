from rest_framework import serializers
from .models import Agent, Photo

class PhotoSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les photos d'un agent."""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Photo
        fields = ['id', 'image', 'uploaded_at', 'image_url']
        read_only_fields = ['uploaded_at']
    
    def get_image_url(self, obj):
        """Retourne l'URL complète de l'image."""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
class AgentProfileSerializer(serializers.ModelSerializer):
    """Sérialiseur étendu pour le profil d'un agent, incluant ses photos."""
    photos = PhotoSerializer(many=True, read_only=True)
    profile_photo = serializers.SerializerMethodField()
    cover_photo = serializers.SerializerMethodField()
    animation_photo = serializers.SerializerMethodField()
    
    class Meta:
        model = Agent
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'age', 'gender', 'location', 'phone_number', 
            'measurements', 'total_payments', 'date_joined',
            'photos', 'profile_photo', 'cover_photo', 'animation_photo'
        ]
        read_only_fields = ['date_joined', 'username', 'total_payments']
    
    def get_profile_photo(self, obj):
        photo = obj.photos.filter(photo_type='profile').first()
        if photo:
            return PhotoSerializer(photo, context=self.context).data
        return None
    
    def get_cover_photo(self, obj):
        photo = obj.photos.filter(photo_type='cover').first()
        if photo:
            return PhotoSerializer(photo, context=self.context).data
        return None
    
    def get_animation_photo(self, obj):
        photo = obj.photos.filter(photo_type='animation').first()
        if photo:
            return PhotoSerializer(photo, context=self.context).data
        return None

class AgentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['id', 'username', 'age', 'gender', 'location', 'phone_number', 'measurements', 'date_joined', 'is_superuser']
        read_only_fields = ['date_joined']
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)  # Gère les cas où `password` est absent
        agent = Agent(**validated_data)
        if password:  # Si un mot de passe est fourni ou généré
            agent.set_password(password)
        agent.save()
        return agent

