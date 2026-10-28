from rest_framework import serializers

from core.models import Skill
from offers.models import Offer, OfferSkill, SavedOffer
from organizations.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "kind"]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "slug"]


class OfferSkillSerializer(serializers.ModelSerializer):
    skill_detail = SkillSerializer(source="skill", read_only=True)
    requirement_display = serializers.CharField(
        source="get_requirement_display",
        read_only=True,
    )

    class Meta:
        model = OfferSkill
        fields = ["id", "skill", "skill_detail", "requirement", "requirement_display"]


class CreatorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    professional_title = serializers.CharField()


class OfferSerializer(serializers.ModelSerializer):
    created_by = CreatorSerializer(read_only=True)
    organization_detail = OrganizationSerializer(source="organization", read_only=True)
    offer_skills = OfferSkillSerializer(many=True, read_only=True)
    modality_display = serializers.CharField(source="get_modality_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    saved_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "organization",
            "organization_detail",
            "created_by",
            "title",
            "slug",
            "description",
            "location",
            "modality",
            "modality_display",
            "status",
            "status_display",
            "salary_min",
            "salary_max",
            "saved_count",
            "offer_skills",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "slug", "created_at"]

    def validate(self, attrs):
        salary_min = attrs.get("salary_min", getattr(self.instance, "salary_min", None))
        salary_max = attrs.get("salary_max", getattr(self.instance, "salary_max", None))
        if salary_min is not None and salary_max is not None and salary_max < salary_min:
            raise serializers.ValidationError(
                {"salary_max": "El salario máximo no puede ser menor que el mínimo."}
            )
        return attrs


class SavedOfferSerializer(serializers.ModelSerializer):
    offer = OfferSerializer(read_only=True)

    class Meta:
        model = SavedOffer
        fields = ["id", "offer", "created_at"]