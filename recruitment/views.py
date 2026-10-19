
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import TaskForm
from .models import Task


@login_required
def task_list(request):
    tasks = Task.objects.filter(owner=request.user)

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "")
    priority = request.GET.get("priority", "")
    task_type = request.GET.get("task_type", "")

    if search:
        tasks = tasks.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
        )

    if status:
        tasks = tasks.filter(status=status)

    if priority:
        tasks = tasks.filter(priority=priority)

    if task_type:
        tasks = tasks.filter(task_type=task_type)

    tasks = tasks.order_by("due_date", "-created_at")

    context = {
        "tasks": tasks,
        "search": search,
        "status_filter": status,
        "priority_filter": priority,
        "task_type_filter": task_type,
        "status_choices": Task.Status.choices,
        "priority_choices": Task.Priority.choices,
        "task_type_choices": Task.TaskType.choices,
    }

    return render(request, "recruitment/task_list.html", context)


@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user

            # Una tarea nueva no puede tener fecha de finalización
            # si no se crea directamente como completada.
            if task.status == Task.Status.COMPLETED:
                task.completed_at = timezone.now()
            else:
                task.completed_at = None

            task.save()

            messages.success(
                request,
                f'La tarea "{task.title}" se ha creado correctamente.',
            )
            return redirect("recruitment:task_list")
    else:
        form = TaskForm()

    return render(
        request,
        "recruitment/task_form.html",
        {"form": form, "page_title": "Crear tarea"},
    )


@login_required
def task_detail(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        owner=request.user,
    )

    return render(
        request,
        "recruitment/task_detail.html",
        {"task": task},
    )


@login_required
def task_update(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        owner=request.user,
    )

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            previous_status = task.status
            task = form.save(commit=False)

            if task.status == Task.Status.COMPLETED:
                if (
                    previous_status != Task.Status.COMPLETED
                    or task.completed_at is None
                ):
                    task.completed_at = timezone.now()
            else:
                task.completed_at = None

            task.save()

            messages.success(
                request,
                f'La tarea "{task.title}" se ha actualizado correctamente.',
            )
            return redirect("recruitment:task_detail", pk=task.pk)
    else:
        form = TaskForm(instance=task)

    return render(
        request,
        "recruitment/task_form.html",
        {
            "form": form,
            "task": task,
            "page_title": "Editar tarea",
        },
    )


@login_required
def task_delete(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        owner=request.user,
    )

    if request.method == "POST":
        title = task.title
        task.delete()

        messages.success(
            request,
            f'La tarea "{title}" se ha eliminado correctamente.',
        )
        return redirect("recruitment:task_list")

    return render(
        request,
        "recruitment/task_confirm_delete.html",
        {"task": task},
    )


@login_required
@require_POST
def task_complete(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        owner=request.user,
    )

    if (
        task.status != Task.Status.COMPLETED
        or task.completed_at is None
    ):
        task.status = Task.Status.COMPLETED
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at"])

    messages.success(
        request,
        f'La tarea "{task.title}" se ha marcado como completada.',
    )

    return redirect("recruitment:task_list")


@login_required
@require_POST
def task_reopen(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        owner=request.user,
    )

    task.status = Task.Status.PENDING
    task.completed_at = None
    task.save(update_fields=["status", "completed_at"])

    messages.success(
        request,
        f'La tarea "{task.title}" se ha reabierto correctamente.',
    )

    return redirect("recruitment:task_list")
