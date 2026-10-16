from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from decimal import Decimal
import random

# Importamos todos los modelos creados en los bloques 2 y 3
from organizations.models import Organization, Skill
from offers.models import Offer, ModalityChoices, StatusChoices
from candidates.models import Candidate, CandidateSkill
# Nota: Si tu modelo de Tareas se llama de otra forma, ajusta la importación
from recruitment.models import Task  

User = get_user_model()

class Command(BaseCommand):
    help = 'Precarga la base de datos con datos de ejemplo para las sesiones'

    def handle(self, *args, **kwargs):
        self.stdout.write('Borrando datos antiguos...')
        # Limpieza en orden inverso de dependencias para evitar errores de claves foráneas
        Task.objects.all().delete()
        CandidateSkill.objects.all().delete()
        Candidate.objects.all().delete()
        Offer.objects.all().delete()
        Skill.objects.all().delete()
        Organization.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write('Creando nuevos datos de ejemplo...')

        # 1. Crear 3 Usuarios
        users = []
        for i in range(1, 4):
            user = User.objects.create_user(
                username=f'usuario{i}',
                email=f'usuario{i}@talentmatch.com',
                password='password123'
            )
            users.append(user)
        self.stdout.write(f'- {len(users)} Usuarios creados.')

        # 2. Crear 2 Organizaciones
        org1 = Organization.objects.create(name="Tech Global", slug="tech-global", kind="empresa")
        org2 = Organization.objects.create(name="Headhunters Alpha", slug="headhunters-alpha", kind="firma de headhunting")
        orgs = [org1, org2]
        self.stdout.write('- 2 Organizaciones creadas.')

        # 3. Crear 8 Skills
        skill_names = ['Python', 'Django', 'React', 'Git', 'Docker', 'PostgreSQL', 'Inglés B2', 'Scrum']
        skills = []
        for name in skill_names:
            skill = Skill.objects.create(name=name, slug=slugify(name), is_active=True)
            skills.append(skill)
        self.stdout.write(f'- {len(skills)} Skills creadas.')

        # 4. Crear 5 Ofertas
        offer_titles = [
            ('Backend Dev (Django)', ModalityChoices.REMOTO, StatusChoices.PUBLICADA, Decimal('40000.00'), Decimal('55000.00')),
            ('Frontend Dev (React)', ModalityChoices.HIBRIDO, StatusChoices.PUBLICADA, Decimal('35000.00'), Decimal('45000.00')),
            ('Fullstack Engineer', ModalityChoices.PRESENCIAL, StatusChoices.BORRADOR, Decimal('45000.00'), Decimal('60000.00')),
            ('DevOps Specialist', ModalityChoices.REMOTO, StatusChoices.PAUSADA, Decimal('50000.00'), Decimal('70000.00')),
            ('Data Analyst Intern', ModalityChoices.REMOTO, StatusChoices.CUBIERTA, Decimal('18000.00'), Decimal('22000.00')),
        ]
        
        for i, (title, mod, stat, s_min, s_max) in enumerate(offer_titles):
            Offer.objects.create(
                organization=random.choice(orgs),
                created_by=users[0],
                title=title,
                slug=slugify(title),
                description=f"Descripción detallada para la posición de {title}.",
                location="Madrid / Remoto",
                modality=mod,
                status=stat,
                salary_min=s_min,
                salary_max=s_max
            )
        self.stdout.write('- 5 Ofertas creadas.')

        # 5. Crear 3 Candidatos y sus CandidateSkills
        for i in range(3):
            candidate = Candidate.objects.create(
                user=users[i],
                availability="Inmediata" if i == 0 else "1 mes",
                interests="Desarrollo de software y arquitectura",
                allows_contact=True
            )
            # Le asignamos 2 skills aleatorias a cada candidato
            for skill in random.sample(skills, 2):
                CandidateSkill.objects.create(
                    candidate=candidate,
                    skill=skill,
                    evidence="Experiencia demostrable en proyectos académicos.",
                    source=CandidateSkill.SourceChoices.PROYECTO
                )
        self.stdout.write('- 3 Candidatos creados (con sus respectivas competencias).')

        # 6. Crear 5 Tareas (Tasks) ligadas a los usuarios
        for i in range(1, 6):
            Task.objects.create(
                user=random.choice(users),
                title=f"Tarea de reclutamiento #{i}",
                description=f"Revisar estado del proceso de selección número {i}."
            )
        self.stdout.write('- 5 Tareas creadas.')
        
        self.stdout.write(self.style.SUCCESS('¡Base de datos populada con éxito!'))
