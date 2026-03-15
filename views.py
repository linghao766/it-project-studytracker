from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse
from django.core import mail

from .models import Reminder, Task

class EmailIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='test@example.com', password='password123')
        self.client.login(username='tester', password='password123')
        self.task = Task.objects.create(user=self.user, title='Test Task')

    def test_reminder_sends_email(self):
        """Test that setting a reminder for a task sends an email notification to the user."""
        # Simulate submitting a form with a reminder time
        url = reverse('task_update', args=[self.task.pk])
        data = {
            'title': 'Test Task',
            'description': 'This is a test description',
            'status': 'pending',
            'reminder-reminder_time': '10:00',
            'reminder-is_active': 'on'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        # Verify that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Study Reminder Confirmed')

class TaskModelTests(TestCase):
    def test_task_defaults_to_pending(self):
        user = User.objects.create_user(username='alice', password='safe-pass-123')
        task = Task.objects.create(user=user, title='Read chapter 1')
        self.assertEqual(task.status, Task.Status.PENDING)
        self.assertFalse(task.is_completed)


class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='bob', password='safe-pass-123')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_toggle_status_returns_json(self):
        self.client.login(username='bob', password='safe-pass-123')
        task = Task.objects.create(user=self.user, title='Prepare notes')
        response = self.client.post(reverse('task_toggle_status', args=[task.pk]))
        task.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(task.status, Task.Status.COMPLETED)
        self.assertEqual(response.json()['status'], Task.Status.COMPLETED)


class ReminderTests(TestCase):
    def test_one_reminder_per_task(self):
        user = User.objects.create_user(username='carol', password='safe-pass-123')
        task = Task.objects.create(user=user, title='Practice SQL')
        Reminder.objects.create(task=task, reminder_time='09:00')
        with self.assertRaises(IntegrityError):
            Reminder.objects.create(task=task, reminder_time='10:00')

