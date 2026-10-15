
from django.db import models
from django.utils.text import slugify


class Skill(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
    )
    description = models.TextField(
        blank=True,
    )
    is_active = models.BooleanField(
    default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    
    class Meta:
        ordering = ["name"]
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
