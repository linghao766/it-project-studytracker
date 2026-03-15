from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    UserLoginView,
    dashboard,
    history,
    home,
    signup,
    task_create,
    task_delete,
    task_toggle_status,
    task_update,
)

urlpatterns = [
    path('', home, name='home'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', signup, name='signup'),
    path('dashboard/', dashboard, name='dashboard'),
    path('history/', history, name='history'),
    path('tasks/new/', task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', task_delete, name='task_delete'),
    path('tasks/<int:pk>/toggle-status/', task_toggle_status, name='task_toggle_status'),
]
