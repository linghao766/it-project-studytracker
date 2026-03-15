from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.core.mail import send_mail

from .forms import LoginForm, ReminderForm, SignUpForm, TaskForm
from .models import Reminder, Task

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    form = TaskForm(request.POST or None, instance=task)
    reminder = getattr(task, 'reminder', None)
    reminder_form = ReminderForm(request.POST or None, instance=reminder, prefix='reminder')

    if request.method == 'POST' and form.is_valid() and reminder_form.is_valid():
        task = form.save()
        reminder_instance = reminder_form.save(commit=False)
        reminder_time = reminder_form.cleaned_data.get('reminder_time')

        if reminder_time:
            reminder_instance.task = task
            reminder_instance.save()
            
            send_mail(
                subject='Study Reminder Confirmed',
                message=f'Hi {request.user.username}, you have set a daily reminder for "{task.title}" at {reminder_time}.',
                from_email=None,  
                recipient_list=[request.user.email],
                fail_silently=False,
            )
        elif reminder:
            reminder.delete()
            
        messages.success(request, 'Task updated and notification sent.')
        return redirect('dashboard')

    context = {
        'form': form,
        'reminder_form': reminder_form,
        'page_title': 'Edit Task',
        'task': task,
    }
    return render(request, 'tracker/task_form.html', context)

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'tracker/home.html')


class UserLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'registration/login.html'


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Your account has been created.')
        return redirect('dashboard')
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    tasks = Task.objects.for_user(request.user).select_related('reminder')
    recent_activity = Task.objects.for_user(request.user).order_by('-updated_at')[:5]
    context = {
        'tasks': tasks,
        'pending_count': tasks.pending().count(),
        'completed_count': tasks.completed().count(),
        'reminder_count': Reminder.objects.filter(task__user=request.user, is_active=True).count(),
        'history_count': tasks.completed().count(),
        'recent_activity': recent_activity,
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def task_create(request):
    form = TaskForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.user = request.user
        task.save()
        messages.success(request, 'Task created successfully.')
        return redirect('dashboard')
    return render(request, 'tracker/task_form.html', {'form': form, 'page_title': 'Add Task'})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted.')
        return redirect('dashboard')
    return render(request, 'tracker/task_confirm_delete.html', {'task': task})


@login_required
@require_POST
def task_toggle_status(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.status = Task.Status.COMPLETED if task.status == Task.Status.PENDING else Task.Status.PENDING
    task.save(update_fields=['status', 'updated_at'])
    return JsonResponse({
        'id': task.pk,
        'status': task.status,
        'status_label': task.get_status_display(),
        'completed_count': Task.objects.for_user(request.user).completed().count(),
        'pending_count': Task.objects.for_user(request.user).pending().count(),
    })


@login_required
def history(request):
    tasks = Task.objects.for_user(request.user).completed().select_related('reminder')
    return render(request, 'tracker/history.html', {'tasks': tasks})

