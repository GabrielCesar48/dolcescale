# Script para inserir cronograma de limpeza única da máquina de café
# Execute com: python manage.py shell
# Em seguida, copie e cole todo o script

from django.utils import timezone
from datetime import datetime, timedelta, date, time
from core.models import TeamMember, DutyType, DutySchedule, Holiday
from django.contrib.auth.models import User
import pytz

# Configuração do fuso horário (Brasil)
tz = pytz.timezone('America/Sao_Paulo')

print("=== CONFIGURAÇÃO DE CRONOGRAMA DE LIMPEZA ÚNICA ===")
print(f"Data de início: {timezone.now().date()}")

# Limpar escalas futuras existentes
hoje = timezone.now().date()
escalas_removidas = DutySchedule.objects.filter(date__gte=hoje).delete()[0]
print(f"Escalas futuras removidas: {escalas_removidas}")

# Recriar os tipos de tarefa para limpeza única
print("\n=== CRIANDO TIPOS DE TAREFA DE LIMPEZA ÚNICA ===")
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

print(f"✓ Criado: {limpeza_1630}")
print(f"✓ Criado: {limpeza_1730}")

# Verificar e criar/atualizar membros da equipe
print("\n=== CONFIGURANDO MEMBROS DA EQUIPE ===")

# Dados dos membros conforme fornecido (excluindo Monark)
membros_data = [
    {
        'username': 'gabriel',
        'email': 'gabrielcesar48@gmail.com',
        'phone': '35988656135',
        'exit_time': time(18, 0),  # Sai às 18:00, limpa às 17:30
        'first_name': 'Gabriel',
        'last_name': 'César'
    },
    {
        'username': 'leonardo',
        'email': 'leonardo.dinizolv@gmail.com', 
        'phone': '',
        'exit_time': time(17, 30),  # Sai às 17:30, limpa às 17:00
        'first_name': 'Leonardo',
        'last_name': 'Diniz'
    },
    {
        'username': 'allan',
        'email': 'cabelin@empresa.com',
        'phone': '',
        'exit_time': time(17, 30),  # Sai às 17:30, limpa às 17:00
        'first_name': 'Allan',
        'last_name': 'Cabelin'
    },
    {
        'username': 'mamada',
        'email': 'mamada@empresa.com',
        'phone': '',
        'exit_time': time(18, 0),   # Sai às 18:00, limpa às 17:30
        'first_name': 'Guilherme',
        'last_name': 'Mamada'
    },
    {
        'username': 'ranielle',
        'email': 'ranielle@empresa.com',
        'phone': '',
        'exit_time': time(17, 0),   # Sai às 17:00, limpa às 16:30
        'first_name': 'Ranielle',
        'last_name': ''
    },
    {
        'username': 'wesley',
        'email': 'wesley@empresa.com',
        'phone': '',
        'exit_time': time(17, 0),   # Sai às 17:00, limpa às 16:30
        'first_name': 'Wesley',
        'last_name': ''
    },
    {
        'username': 'juliano',
        'email': 'juliano@empresa.com',
        'phone': '',
        'exit_time': time(18, 0),   # Sai às 18:00, limpa às 17:30
        'first_name': 'Juliano',
        'last_name': ''
    }
]

# Criar/atualizar usuários e membros
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
        
        # Criar ou atualizar TeamMember
        team_member, member_created = TeamMember.objects.update_or_create(
            user=user,
            defaults={
                'email': membro_data['email'],
                'phone': membro_data['phone'],
                'exit_time': membro_data['exit_time'],
                'cleaning_preference': 'auto',  # Automático: 30min antes da saída
                'is_active': True
            }
        )
        
        membros_ativos.append(team_member)
        
        status = "criado" if member_created else "atualizado"
        cleaning_time = team_member.get_cleaning_time_display()
        exit_time = team_member.get_exit_time_display()
        
        print(f"✓ {team_member} {status} - Sai: {exit_time}, Limpa: {cleaning_time}")
        
    except Exception as e:
        print(f"❌ Erro ao processar {membro_data['username']}: {str(e)}")

print(f"\n📊 Total de membros ativos: {len(membros_ativos)}")

# Desativar Monark se existir
try:
    monark_user = User.objects.get(username='monark')
    monark_member = TeamMember.objects.get(user=monark_user)
    monark_member.is_active = False
    monark_member.save()
    print("⚠️  Monark desativado conforme solicitado")
except:
    print("ℹ️  Monark não encontrado (já removido)")

# Função para escolher o tipo de limpeza baseado no horário de saída do membro
def escolher_tipo_limpeza(membro):
    """Retorna o tipo de limpeza ideal baseado no horário de saída"""
    cleaning_time = membro.get_cleaning_time()
    
    # Se limpa antes das 17:00, usa o horário 16:30
    # Se limpa às 17:00 ou depois, usa o horário 17:30
    if cleaning_time.hour < 17:
        return limpeza_1630
    else:
        return limpeza_1730

# Gerar cronograma para os próximos 30 dias
print("\n=== GERANDO CRONOGRAMA PARA 30 DIAS ===")

cronograma_criado = []
registros_criados = 0
data_atual = hoje
membro_index = 0

# Ordenar membros por horário de limpeza para rotação balanceada
membros_ordenados = sorted(membros_ativos, key=lambda m: m.get_cleaning_time())
print("Ordem de rotação:")
for i, membro in enumerate(membros_ordenados):
    print(f"  {i+1}. {membro} (limpa às {membro.get_cleaning_time_display()})")

for dia in range(30):
    data_limpeza = data_atual + timedelta(days=dia)
    
    # Pular fins de semana (sábado=5, domingo=6)
    if data_limpeza.weekday() >= 5:
        print(f"⊗ {data_limpeza.strftime('%d/%m (%a)')} - Pulado (fim de semana)")
        continue
    
    # Verificar se é feriado
    if Holiday.objects.filter(date=data_limpeza).exists():
        feriado = Holiday.objects.get(date=data_limpeza)
        print(f"🎉 {data_limpeza.strftime('%d/%m (%a)')} - Pulado (feriado: {feriado.name})")
        continue
    
    # Escolher membro da rotação
    membro_responsavel = membros_ordenados[membro_index % len(membros_ordenados)]
    tipo_limpeza = escolher_tipo_limpeza(membro_responsavel)
    
    # Criar escala
    try:
        schedule, created = DutySchedule.objects.update_or_create(
            date=data_limpeza,
            defaults={
                'member': membro_responsavel,
                'duty_type': tipo_limpeza,
                'completed': False,  # Todas como pendentes
                'notification_sent': False
            }
        )
        
        if created:
            registros_criados += 1
            
        cronograma_criado.append({
            'data': data_limpeza,
            'membro': membro_responsavel,
            'tipo': tipo_limpeza,
            'novo': created
        })
        
        status_icon = "✓" if created else "↻"
        print(f"{status_icon} {data_limpeza.strftime('%d/%m (%a)')} - {membro_responsavel} às {tipo_limpeza.time.strftime('%H:%M')}")
        
        # Avançar para próximo membro
        membro_index += 1
        
    except Exception as e:
        print(f"❌ Erro ao criar escala para {data_limpeza}: {str(e)}")

print(f"\n=== RESUMO FINAL ===")
print(f"📅 Período: {hoje.strftime('%d/%m/%Y')} a {(hoje + timedelta(days=29)).strftime('%d/%m/%Y')}")
print(f"✓ {registros_criados} novas limpezas agendadas")
print(f"👥 {len(membros_ativos)} membros na rotação")

# Estatísticas por horário
limpezas_1630 = sum(1 for item in cronograma_criado if item['tipo'] == limpeza_1630)
limpezas_1730 = sum(1 for item in cronograma_criado if item['tipo'] == limpeza_1730)

print(f"\n⏰ DISTRIBUIÇÃO POR HORÁRIO:")
print(f"🕐 16:30: {limpezas_1630} limpezas")
print(f"🕕 17:30: {limpezas_1730} limpezas")

# Estatísticas por membro
print(f"\n👥 DISTRIBUIÇÃO POR MEMBRO:")
for membro in membros_ordenados:
    count = sum(1 for item in cronograma_criado if item['membro'] == membro)
    horario_ideal = membro.get_cleaning_time_display()
    print(f"   {membro}: {count} limpezas (ideal: {horario_ideal})")

# Próximas 5 limpezas
print(f"\n📅 PRÓXIMAS 5 LIMPEZAS:")
proximas = sorted(cronograma_criado, key=lambda x: x['data'])[:5]
for item in proximas:
    data_str = item['data'].strftime('%d/%m (%a)')
    horario = item['tipo'].time.strftime('%H:%M')
    print(f"   {data_str} às {horario} - {item['membro']}")

print(f"\n🎉 Cronograma de limpeza única configurado com sucesso!")
print("💡 Agora cada dia tem apenas uma pessoa responsável pela limpeza completa")
print("📱 Os horários foram otimizados baseados no horário de saída de cada pessoa")
print("🔧 Acesse o perfil individual para ajustar horários pessoais se necessário")