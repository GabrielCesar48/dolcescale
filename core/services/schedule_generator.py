# core/services/schedule_generator.py

from datetime import datetime, timedelta
from django.utils import timezone
from core.models import TeamMember, DutyType, DutySchedule, Holiday
import logging

logger = logging.getLogger(__name__)

class ScheduleGenerator:
    """Serviço para gerar a escala de manutenção da máquina de café"""
    
    def __init__(self, start_date=None, days_to_generate=30):
        """
        Inicializa o gerador de escala
        
        Args:
            start_date: Data inicial para geração (se None, usa a data atual)
            days_to_generate: Número de dias a serem gerados a partir da data inicial
        """
        self.start_date = start_date or timezone.now().date()
        self.days_to_generate = days_to_generate
    
    def generate_schedule(self):
        """Gera a escala de manutenção para os próximos dias"""
        
        # Busca membros ativos
        active_members = list(TeamMember.objects.filter(is_active=True))
        if not active_members:
            logger.warning("Nenhum membro ativo encontrado para gerar escala")
            return False
        
        # Busca tipos de tarefas
        duty_types = list(DutyType.objects.all())
        if not duty_types:
            logger.warning("Nenhum tipo de tarefa encontrado para gerar escala")
            return False
        
        # Busca feriados no período
        end_date = self.start_date + timedelta(days=self.days_to_generate)
        holidays = Holiday.objects.filter(
            date__gte=self.start_date,
            date__lte=end_date
        ).values_list('date', flat=True)
        
        # Busca última escala para continuar a rotação
        last_schedule = DutySchedule.objects.order_by('-date', '-duty_type__time').first()
        
        # Define o índice inicial do membro (continuando a partir do último)
        if last_schedule:
            try:
                last_member_index = active_members.index(last_schedule.member)
                current_member_index = (last_member_index + 1) % len(active_members)
            except ValueError:
                # Se o último membro não estiver mais ativo
                current_member_index = 0
        else:
            current_member_index = 0
            
        # Contador para armazenar escalas criadas
        created_count = 0
            
        # Gera escala para cada dia no período
        current_date = self.start_date
        while current_date <= end_date:
            # Verifica se não é final de semana (0=segunda, 6=domingo) ou feriado
            if current_date.weekday() < 5 and current_date not in holidays:
                for duty_type in duty_types:
                    # Verifica se já existe escala para este dia e tipo
                    if not DutySchedule.objects.filter(date=current_date, duty_type=duty_type).exists():
                        # Cria a nova escala
                        member = active_members[current_member_index]
                        DutySchedule.objects.create(
                            member=member,
                            duty_type=duty_type,
                            date=current_date
                        )
                        created_count += 1
                        
                        # Avança para o próximo membro na rotação
                        current_member_index = (current_member_index + 1) % len(active_members)
                    
                    # Se for criar mais de um tipo de tarefa por dia, 
                    # usar o mesmo membro para todas as tarefas do dia:
                    # current_member_index = (current_member_index - 1) % len(active_members)
            
            # Avança para o próximo dia
            current_date += timedelta(days=1)
            
        return created_count