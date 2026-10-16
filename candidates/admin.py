from django.contrib import admin
from .models import Candidate

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    # Columnas visibles en el listado
    list_display = ('user', 'allows_contact')
    # Filtro lateral por el estado de contacto
    list_filter = ('allows_contact',)
    # Buscador que accede a los datos del modelo User relacionado (usando el doble guion bajo __)
    search_fields = ('user__username', 'user__email', 'interests')
