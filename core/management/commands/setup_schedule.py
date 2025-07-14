# core/management/commands/setup_schedule.py

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta, date, time
from core.models import TeamMember, DutyType, DutySchedule, Holiday
from django.contrib.auth.models import User
import pytz

class Command(BaseCommand):
    help = 'Configura o cronograma de limpeza única da máquina de café'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Número de dias para gerar (padrão: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove escalas futuras antes de criar novas'
        )
        parser.add_argument(
            '--reset-types',
            action='store_true',
            help='Recria os tipos de tarefa'
        )

    def handle(self, *args, **options):
        self.stdout.write("=== CONFIGURAÇÃO DE CRONOGRAMA DE LIMPEZA ÚNICA ===")
        
        days = options['days']
        should_clear = options['clear']
        should_reset_types = options['reset_types']
        
        hoje = timezone.now().date()
        self.stdout.write(f"Data de início: {hoje}")
        
        # Limpar escalas futuras se solicitado
        if should_clear:
            escalas_removidas = DutySchedule.objects.filter(date__gte=hoje).delete()[0]
            self.stdout.write(f"Escalas futuras removidas: {escalas_removidas}")
        
        # Recriar tipos de tarefa se solicitado
        if should_reset_types:
            self.setup_duty_types()
        
        # Configurar membros
        membros_ativos = self.setup_team_members()
        
        # Gerar cronograma
        self.generate_schedule(hoje, days, membros_ativos)
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Cronograma configurado com sucesso!')
        )
    
    def setup_duty_types(self):
        """Configura os tipos de tarefa de limpeza"""
        self.stdout.write("\n=== CONFIGURANDO TIPOS DE TAREFA ===")
        
        DutyType.objects.all().delete()
        
        limpeza_1630 = DutyType.objects.create(
            name="Limpeza Completa - 16:30",
            time="16:30:00",
            description="Limpeza completa da máquina de café para quem sai às 17:00"
        )
        
        limpeza_1730 = DutyType.objects.create(
            name="Limpeza Completa - 17:30", 
            time="17:30:00",
            description="Limpeza completa da máquina de café para quem sai às 18:00"
        )
        
        self.stdout.write(f"✓ Criado: {limpeza_1630}")
        self.stdout.write(f"✓ Criado: {limpeza_1730}")
        
        return limpeza_1630, limpeza_1730
    
    def setup_team_members(self):
        """Configura os membros da equipe"""
        self.stdout.write("\n=== CONFIGURANDO MEMBROS DA EQUIPE ===")
        
        # Dados dos membros (sem Monark)
        membros_data = [
            {
                'username': 'gabriel',
                'email': 'gabrielcesar48@gmail.com',
                'phone': '35988656135',
                'exit_time': time(18, 0),
                'first_name': 'Gabriel',
                'last_name': 'César'
            },
            {
                'username': 'leonardo',
                'email': 'leonardo.dinizolv@gmail.com', 
                'phone': '',
                'exit_time': time(17, 30),
                'first_name': 'Leonardo',
                'last_name': 'Diniz'
            },
            {
                'username': 'allan',
                'email': 'cabelin@empresa.com',
                'phone': '',
                'exit_time': time(17, 30),
                'first_name': 'Allan',
                'last_name': 'Cabelin'
            },
            {
                'username': 'mamada',
                'email': 'mamada@empresa.com',
                'phone': '',
                'exit_time': time(18, 0),
                'first_name': 'Guilherme',
                'last_name': 'Mamada'
            },
            {
                'username': 'ranielle',
                'email': 'ranielle@empresa.com',
                'phone': '',
                'exit_time': time(17, 0),
                'first_name': 'Ranielle',
                'last_name': ''
            },
            {
                'username': 'wesley',
                'email': 'wesley@empresa.com',
                'phone': '',
                'exit_time': time(17, 0),
                'first_name': 'Wesley',
                'last_name': ''
            },
            {
                'username': 'juliano',
                'email': 'juliano@empresa.com',
                'phone': '',
                'exit_time': time(18, 0),
                'first_name': 'Juliano',
                'last_name': ''
            }
        ]
        
        membros_ativos = []
        
        for membro_data in membros_data:
            try:
                # Criar ou atualizar usuário
                user, user_created = User.objects.update_or_create(
                    username=membro_data['username'],
                    defaults={
                        'email': membro_data['email'],
                        'first_name': membro_data['first_name'],
                        'last_name': membro_data['last_name'],
                        'is_active': True
                    }
                )
                
                # Definir senha padrão se for novo usuário
                if user_created:
                    user.set_password('dolcescale2025')
                    user.save()
                
                # Criar ou atualizar TeamMember
                team_member, member_created = TeamMember.objects.update_or_create(
                    user=user,
                    defaults={
                        'email': membro_data['email'],
                        'phone': membro_data['phone'],
                        'exit_time': membro_data['exit_time'],
                        'cleaning_preference': 'auto',
                        'is_active': True
                    }
                )
                
                membros_ativos.append(team_member)
                
                status = "criado" if member_created else "atualizado"
                cleaning_time = team_member.get_cleaning_time_display()
                exit_time = team_member.get_exit_time_display()
                
                self.stdout.write(f"✓ {team_member} {status} - Sai: {exit_time}, Limpa: {cleaning_time}")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erro ao processar {membro_data['username']}: {str(e)}")
                )
        
        # Desativar Monark se existir
        try:
            monark_user = User.objects.get(username='monark')
            monark_member = TeamMember.objects.get(user=monark_user)
            monark_member.is_active = False
            monark_member.save()
            self.stdout.write("⚠️  Monark desativado")
        except:
            pass
        
        self.stdout.write(f"📊 Total de membros ativos: {len(membros_ativos)}")
        return membros_ativos
    
    def escolher_tipo_limpeza(self, membro):
        """Escolhe o tipo de limpeza baseado no horário do membro"""
        cleaning_time = membro.get_cleaning_time()
        
        if cleaning_time.hour < 17:
            return DutyType.objects.get(time__hour=16)  # 16:30
        else:
            return DutyType.objects.get(time__hour=17)  # 17:30
    
    def generate_schedule(self, hoje, days, membros_ativos):
        """Gera o cronograma de limpeza"""
        self.stdout.write(f"\n=== GERANDO CRONOGRAMA PARA {days} DIAS ===")
        
        # Ordenar membros por horário de limpeza
        membros_ordenados = sorted(membros_ativos, key=lambda m: m.get_cleaning_time())
        
        self.stdout.write("Ordem de rotação:")
        for i, membro in enumerate(membros_ordenados):
            self.stdout.write(f"  {i+1}. {membro} (limpa às {membro.get_cleaning_time_display()})")
        
        cronograma_criado = []
        registros_criados = 0
        membro_index = 0
        
        for dia in range(days):
            data_limpeza = hoje + timedelta(days=dia)
            
            # Pular fins de semana
            if data_limpeza.weekday() >= 5:
                continue
            
            # Verificar feriados
            if Holiday.objects.filter(date=data_limpeza).exists():
                continue
            
            # Escolher membro e tipo
            membro_responsavel = membros_ordenados[membro_index % len(membros_ordenados)]
            tipo_limpeza = self.escolher_tipo_limpeza(membro_responsavel)
            
            # Criar escala
            try:
                schedule, created = DutySchedule.objects.update_or_create(
                    date=data_limpeza,
                    defaults={
                        'member': membro_responsavel,
                        'duty_type': tipo_limpeza,
                        'completed': False,
                        'notification_sent': False
                    }
                )
                
                if created:
                    registros_criados += 1
                
                cronograma_criado.append({
                    'data': data_limpeza,
                    'membro': membro_responsavel,
                    'tipo': tipo_limpeza
                })
                
                status_icon = "✓" if created else "↻"
                self.stdout.write(
                    f"{status_icon} {data_limpeza.strftime('%d/%m (%a)')} - "
                    f"{membro_responsavel} às {tipo_limpeza.time.strftime('%H:%M')}"
                )
                
                membro_index += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erro ao criar escala para {data_limpeza}: {str(e)}")
                )
        
        # Relatório final
        self.stdout.write(f"\n=== RESUMO ===")
        self.stdout.write(f"✓ {registros_criados} novas limpezas agendadas")
        
        # Estatísticas por horário
        limpezas_1630 = sum(1 for item in cronograma_criado if item['tipo'].time.hour == 16)
        limpezas_1730 = sum(1 for item in cronograma_criado if item['tipo'].time.hour == 17)
        
        self.stdout.write(f"🕐 16:30: {limpezas_1630} limpezas")
        self.stdout.write(f"🕕 17:30: {limpezas_1730} limpezas")
        
        # Próximas 5 limpezas
        self.stdout.write(f"\n📅 PRÓXIMAS 5 LIMPEZAS:")
        proximas = sorted(cronograma_criado, key=lambda x: x['data'])[:5]
        for item in proximas:
            data_str = item['data'].strftime('%d/%m (%a)')
            horario = item['tipo'].time.strftime('%H:%M')
            self.stdout.write(f"   {data_str} às {horario} - {item['membro']}")