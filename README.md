# Talent Match

Plataforma para que empresas y headhunters descubran talento y gestionen el proceso de selección. La inteligencia artificial ayuda a encontrar candidatos y a explicar su encaje con cada oferta. El headhunter conserva siempre la decisión sobre a quién seleccionar.

Proyecto del módulo UF2406 Ciclo de vida de un proyecto de desarrollo web. Metodología Scrum y desarrollo por fases.

## Estado del proyecto

Sprint 1, Sesión 1 (PB-01) Análisis, requisitos y creación del proyecto.

Hecho en esta sesión
* Documento de requisitos (SRS) con casos de uso, historias de usuario y criterios Gherkin.
* Entorno virtual de Python y repositorio Git con .gitignore.
* Proyecto Django config y apps base core, accounts y offers.

Pendiente para las siguientes sesiones
* Sesión 2, settings por entornos, variables de entorno, conexión a PostgreSQL y modelo accounts.User.
* Sesión 3, perfiles, formularios, registro, login, logout y edición de perfil.

## Tecnologías

* Python y Django
* PostgreSQL como base de datos
* Git con Git Flow y Pull Requests

## Estructura del proyecto

```
TalentMatch/
  config/       configuración del proyecto Django
  core/         funcionalidad común
  accounts/     usuarios, perfiles y autenticación
  offers/       ofertas de trabajo (equivalente a products)
  docs/         documentación del proyecto
  manage.py
  requirements.txt
```

## Puesta en marcha

Requisitos previos, Python 3.10 o superior, Git y PostgreSQL instalado.

```
git clone https://github.com/TalentMatchProject/TalentMatch.git
cd TalentMatch
git checkout develop
python -m venv .venv
```

Activar el entorno virtual.

En Windows (PowerShell)

```
.venv\Scripts\activate
```

En Linux o macOS

```
source .venv/bin/activate
```

Instalar dependencias.

```
pip install -r requirements.txt
```

Crear la base de datos en PostgreSQL.

```
psql -U postgres
CREATE DATABASE talentmatch;
\q
```

Copiar el archivo de ejemplo de variables de entorno y rellenar tus datos (disponible a partir de la Sesión 2).

```
copy .env.example .env
```

Aplicar migraciones y arrancar.

```
python manage.py migrate
python manage.py runserver
```

La aplicación queda disponible en http://127.0.0.1:8000

## Alcance

Incluido
* Gestión de empresas, headhunters y equipos, con permisos por organización.
* Publicación de ofertas con salario, ubicación, modalidad y competencias imprescindibles y deseables.
* Asistente de IA para redactar ofertas a partir de una necesidad.
* Matching explicado con evidencias de encaje, requisitos pendientes y datos por verificar.
* Búsqueda de candidatos por habilidades demostradas, disponibilidad e intereses.
* Listas de candidatos por oferta, con notas y colaboración entre recruiters.
* Seguimiento tipo CRM del proceso de selección.
* Tareas y recordatorios.
* Portal del candidato.
* Analítica del proceso con tiempos, conversiones y motivos de descarte.
* Preparar entrevista y candidatura con identidad oculta en la primera revisión.

Excluido
* Gestión de nóminas y pagos de salarios.
* Videollamadas dentro de la aplicación.
* Entornos de realidad virtual.
* Exámenes automáticos para candidatos.
* Decisiones automáticas de descarte o contratación.

## Actores

* Administrador de organización, gestiona la organización, sus equipos, miembros y roles.
* Headhunter, busca candidatos, valora su encaje, gestiona el pipeline y decide a quién seleccionar.
* Recruiter de empresa, publica ofertas de su organización y colabora en el seguimiento de candidatos.
* Candidato, mantiene su perfil, disponibilidad y preferencias, y consulta el estado de sus candidaturas.
* Sistema de IA, redacta ofertas, calcula el encaje, genera explicaciones y propone preguntas de entrevista. No toma decisiones.

## Casos de uso

* CU01 Gestionar organización
* CU02 Publicar oferta
* CU03 Encontrar candidatos
* CU04 Gestionar lista y pipeline
* CU05 Preparar entrevista
* CU06 Gestionar tareas
* CU07 Consultar candidatura
* CU08 Analizar proceso

## Pipeline de selección

Todas las historias y pantallas usan el mismo conjunto de etapas.

1. Identificado
2. Contacto
3. Entrevista
4. Prueba
5. Oferta
6. Contratado

Descartado es un estado terminal que se puede alcanzar desde cualquier etapa y exige un motivo de descarte.

## Requisitos funcionales

Must
* RF01 Autenticación de usuarios y permisos por organización y rol.
* RF02 CRUD de empresas, headhunters y equipos.
* RF03 CRUD de ofertas con salario, ubicación, modalidad y competencias.
* RF04 Registro de candidatos con habilidades, evidencias, disponibilidad e intereses.
* RF05 Lista de candidatos por oferta con notas compartidas.
* RF06 Pipeline con etapas, historial de cambios y motivo de descarte.
* RF07 Matching explicado por requisito, con estados demostrado, pendiente y por verificar.

Should
* RF08 Asistente de IA para redactar ofertas.
* RF09 Búsqueda semántica con embeddings y similitud coseno.
* RF10 Búsqueda por habilidades demostradas, disponibilidad e intereses.
* RF11 Tareas y recordatorios vinculados a candidaturas.
* RF12 Preparar entrevista con preguntas sobre requisitos no demostrados.
* RF13 Actualización del pipeline en tiempo real mediante WebSockets.

Could
* RF14 Candidatura con identidad oculta en la primera revisión.
* RF15 Portal del candidato.
* RF16 Analítica de tiempos, conversiones y motivos de descarte.
* RF17 Asistente de screening conversacional para candidatos.

## Requisitos no funcionales

* RNF01 Seguridad. Autenticación obligatoria y control de acceso por organización y rol.
* RNF02 Privacidad. Consentimiento del candidato, caducidad de datos y registro de accesos conforme al RGPD.
* RNF03 Explicabilidad. Todo resultado de IA muestra su justificación y puede ser corregido por una persona.
* RNF04 Equidad. La IA no usa datos personales protegidos para calcular el encaje.
* RNF05 Rendimiento. La lista de candidatos de una oferta se muestra en menos de 3 segundos con 500 candidatos.
* RNF06 Mantenibilidad. Tests unitarios y de integración, y configuración sensible fuera del repositorio.
* RNF07 Localización. Interfaz en español y zona horaria Europe/Madrid.

## Historias de usuario y priorización MoSCoW

Must, HU01, HU02, HU04, HU05, HU08 y HU09.
Should, HU03, HU06, HU07, HU10, HU11 y HU12.
Could, HU13, HU14, HU15 y HU16.
Won't, pagos, videollamadas, realidad virtual, exámenes automáticos y decisiones automáticas de descarte o contratación.

El detalle de cada historia con sus criterios de aceptación en Gherkin está en el documento SRS de la carpeta docs.

## Modelo de datos inicial

* Organization, empresa o firma de headhunting.
* Membership, relación entre usuario, organización, equipo y rol.
* Offer, oferta con salario, ubicación, modalidad y estado.
* Skill, catálogo de competencias.
* OfferSkill, competencia de una oferta, imprescindible o deseable.
* Candidate, persona con disponibilidad, intereses y preferencias de contacto.
* CandidateSkill, competencia de un candidato con su evidencia y fuente.
* Application, candidatura de un candidato a una oferta, con etapa, valor de encaje y modo de identidad oculta.
* RequirementAssessment, estado de cada requisito en una candidatura.
* StageHistory, historial de cambios de etapa con autor, fecha y motivo de descarte.
* Note, nota de un recruiter sobre una candidatura.
* Task, tarea o recordatorio vinculado a una candidatura.
* AccessLog, registro de revelado de datos personales.

## Backlog inicial

* E1 Autenticación, organizaciones y permisos (HU01)
* E2 Ofertas y asistente de redacción (HU02, HU03)
* E3 Candidatos, evidencias y listas (HU04, HU08)
* E4 Matching y búsqueda (HU05, HU06, HU07)
* E5 Pipeline y colaboración en tiempo real (HU09, HU10)
* E6 Tareas y recordatorios (HU11)
* E7 Preparar entrevista (HU12)
* E8 Privacidad e identidad oculta (HU13)
* E9 Portal del candidato y screening (HU14, HU16)
* E10 Analítica (HU15)

## Definition of Ready

* La historia tiene rol, acción y beneficio claros.
* Tiene criterios de aceptación en Gherkin.
* Está estimada por el equipo y priorizada con MoSCoW.
* Sus dependencias de datos y de otras historias están identificadas.
* Si incluye IA, define qué datos lee el sistema y cómo se explica el resultado.

## Definition of Done

* El código pasa la revisión de Pull Request en Git.
* Cumple los estándares de arquitectura del proyecto.
* Tiene tests unitarios y de integración que cubren los criterios Gherkin.
* Respeta los permisos por organización.
* Si incluye IA, muestra su justificación y permite la corrección humana.
* El ticket está cerrado en el tablero Kanban.

## Tablero del proyecto

Columnas del tablero Kanban, Backlog, Por hacer, Haciendo, Revisión y Terminado.

## Flujo de trabajo con Git

Se sigue Git Flow.

* No se hacen commits directos a main.
* El trabajo se hace en ramas feature/nombre-de-la-tarea creadas desde develop.
* Cada rama se integra mediante Pull Request y la revisa otro miembro del equipo.
* Los commits siguen convención semántica, por ejemplo feat, fix, chore, docs y refactor.
* No se suben al repositorio los archivos .env, db.sqlite3, __pycache__ ni .venv.

Ejemplo

```
git checkout develop
git pull
git checkout -b feature/nombre-de-la-tarea
git commit -m "feat: descripción del cambio"
git push -u origin feature/nombre-de-la-tarea
```

## Equipo

Diego, Cristofer, Annia