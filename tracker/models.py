from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class TaskQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)

    def completed(self):
        return self.filter(status=Task.Status.COMPLETED)

    def pending(self):
        return self.filter(status=Task.Status.PENDING)


class Task(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TaskQuerySet.as_manager()

    class Meta:
        ordering = ['status', 'due_date', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED


class Reminder(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='reminder')
    reminder_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['reminder_time']

    def __str__(self):
        return f'Reminder for {self.task.title}'

    def clean(self):
        if self.task_id and self.task.user_id and self.task.is_completed and self.is_active:
            raise ValidationError('Completed tasks cannot have active reminders.')

    def next_reminder_label(self):
        current = timezone.localtime()
        scheduled = current.replace(
            hour=self.reminder_time.hour,
            minute=self.reminder_time.minute,
            second=0,
            microsecond=0,
        )
        if scheduled < current:
            scheduled += timedelta(days=1)
        return scheduled.strftime('%a %d %b, %H:%M')

# Create your models here.
