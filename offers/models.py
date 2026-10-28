from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.text import slugify

# Opciones de modalidad
class ModalityChoices(models.TextChoices):
    PRESENCIAL = 'presencial', 'Presencial'
    HIBRIDO = 'hibrido', 'Híbrido'
    REMOTO = 'remoto', 'Remoto'

# Opciones de estado
class StatusChoices(models.TextChoices):
    BORRADOR = 'borrador', 'Borrador'
    PUBLICADA = 'publicada', 'Publicada'
    PAUSADA = 'pausada', 'Pausada'
    CERRADA = 'cerrada', 'Cerrada'
    CUBIERTA = 'cubierta', 'Cubierta'

class Offer(models.Model):
    # Relaciones obligatorias
    # PROTECT impide borrar una organización si esta tiene ofertas vigentes
    organization = models.ForeignKey('organizations.Organization', on_delete=models.PROTECT, related_name='offers')
    # Si se borra el usuario, el campo se queda vacío (NULL)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Campos de texto principales
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    location = models.CharField(max_length=255)
    
    # Selectores (Choices) con valores por defecto
    modality = models.CharField(max_length=20, choices=ModalityChoices.choices, default=ModalityChoices.PRESENCIAL)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.BORRADOR)
    
    # Salarios opcionales (null y blank) y validados para no ser negativos (mínimo 0.00)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.00'))])
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.00'))])
    
    # Fecha de creación automática
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ordenación por fecha descendente (los más nuevos primero)
        ordering = ['-created_at']
        # Índices en la base de datos para optimizar búsquedas por estado y fecha
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "oferta"
            slug, n = base, 2
            while Offer.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class OfferSkillRequirement(models.TextChoices):
    MUST_HAVE = "must_have", "Obligatoria"
    DESIRABLE = "desirable", "Deseable"

class OfferSkill(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='offer_skills')
    skill = models.ForeignKey('core.Skill', on_delete=models.PROTECT, related_name='offer_skills')
    requirement = models.CharField(
        max_length=20, 
        choices=OfferSkillRequirement.choices, 
        default=OfferSkillRequirement.MUST_HAVE
    )

    class Meta:
        unique_together = ('offer', 'skill')

    def __str__(self):
        return f"{self.skill.name} - {self.offer.title}"

class SavedOffer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_offers",
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="saved_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "offer"],
                name="unique_saved_offer",
            ),
        ]

    def __str__(self):
        return f"{self.user} guarda {self.offer}"