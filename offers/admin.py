from django.contrib import admin
from .models import Offer

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    # Columnas que se verán en el listado principal
    list_display = ('title', 'organization', 'modality', 'status', 'created_at')
    # Filtros accesibles en la barra lateral derecha
    list_filter = ('status', 'modality', 'created_at', 'organization')
    # Barra de búsqueda por texto
    search_fields = ('title', 'description', 'location')
    # Convierte automáticamente el título a formato slug en tiempo real al escribir
    prepopulated_fields = {'slug': ('title',)}

