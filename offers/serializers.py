from rest_framework import serializers
from .models import Offer, OfferSkill

class OfferSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = OfferSkill
        fields = ['id', 'skill_name', 'requirement']

class OfferSerializer(serializers.ModelSerializer):
    # Incluimos las competencias asociadas como un listado anidado (relación inversa)
    offer_skills = OfferSkillSerializer(many=True, read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'organization', 'organization_name', 'title', 'slug', 
            'description', 'location', 'modality', 'status', 
            'salary_min', 'salary_max', 'offer_skills', 'created_at'
        ]
        # El slug se suele generar automáticamente en el backend, lo dejamos de solo lectura
        read_only_fields = ['slug', 'created_at']
