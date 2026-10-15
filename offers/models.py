from django.db import models

class OfferSkillRequirement(models.TextChoices):
    MUST_HAVE = "must_have", "Obligatoria"
    DESIRABLE = "desirable", "Deseable"
