from django import template
from django.utils import timezone

register = template.Library()

@register.simple_tag
def current_time():
    """Retorna a hora atual"""
    return timezone.now().time()

@register.filter
def is_time_now_or_past(time_value):
    """Verifica se o horário é agora ou já passou"""
    current = timezone.now().time()
    return current >= time_value
