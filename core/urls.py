# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('cronograma/', views.schedule_view, name='schedule'),
    path('feriados/', views.holiday_list, name='holiday_list'),
    path('feriados/novo/', views.holiday_create, name='holiday_create'),
    path('feriados/editar/<int:pk>/', views.holiday_edit, name='holiday_edit'),
    path('tarefa/marcar/<int:duty_id>/', views.mark_completed, name='mark_completed'),
]