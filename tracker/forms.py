from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Reminder, Task


class StyledFormMixin:
    def _apply_base_classes(self):
        for field in self.fields.values():
            css_class = 'form-check-input' if isinstance(field.widget, forms.CheckboxInput) else 'form-control'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing} {css_class}'.strip()


class SignUpForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Use a valid email address for account recovery.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_classes()
        self.fields['username'].widget.attrs['autocomplete'] = 'username'
        self.fields['email'].widget.attrs['autocomplete'] = 'email'


class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_classes()
        self.fields['username'].widget.attrs['autocomplete'] = 'username'
        self.fields['password'].widget.attrs['autocomplete'] = 'current-password'


class TaskForm(StyledFormMixin, forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = Task
        fields = ('title', 'description', 'due_date', 'status')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_classes()


class ReminderForm(StyledFormMixin, forms.ModelForm):
    reminder_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text='Leave blank if this task does not need a daily reminder.',
    )

    class Meta:
        model = Reminder
        fields = ('reminder_time', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_classes()

    def clean(self):
        cleaned_data = super().clean()
        reminder_time = cleaned_data.get('reminder_time')
        is_active = cleaned_data.get('is_active')
        if is_active and not reminder_time:
            self.add_error('reminder_time', 'Set a time before activating the reminder.')
        return cleaned_data
