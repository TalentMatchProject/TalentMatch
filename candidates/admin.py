from django.contrib import admin
from .models import Candidate, CandidateSkill

class CandidateSkillInline(admin.TabularInline):
    model = CandidateSkill
    extra = 1

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('user', 'allows_contact')
    list_filter = ('allows_contact',)
    search_fields = ('user__username', 'user__email', 'interests')
    inlines = [CandidateSkillInline]  # <-- Restaurado el Inline oficial


