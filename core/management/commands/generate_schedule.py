# core/management/commands/generate_schedule.py

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from core.services.schedule_generator import ScheduleGenerator
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Gera automaticamente a escala de manutenção da máquina de café'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Número de dias para gerar a escala (padrão: 30)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a geração mesmo que já existam escalas para o período'
        )

    def handle(self, *args, **options):
        days = options['days']
        
        self.stdout.write(f"Gerando escala para os próximos {days} dias...")
        
        generator = ScheduleGenerator(days_to_generate=days)
        created = generator.generate_schedule()
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"Sucesso! {created} escalas geradas."))
        else:
            self.stdout.write(self.style.WARNING("Nenhuma escala foi gerada. Verifique se existem membros ativos e tipos de tarefa configurados."))