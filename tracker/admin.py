from django.contrib import admin

from .models import Reminder, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'user__username')


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ('task', 'reminder_time', 'is_active')
    list_filter = ('is_active',)

# Register your models here.
