# Script para inserir cronograma de escala da máquina de café
# Execute com: python manage.py shell
# Em seguida, copie e cole todo o script

from django.utils import timezone
from datetime import datetime, timedelta, date
from core.models import TeamMember, DutyType, DutySchedule, Holiday
import pytz

# Configuração do fuso horário (Brasil)
tz = pytz.timezone('America/Sao_Paulo')

# Apagar escalas futuras (opcional - remova o comentário se quiser limpar as escalas futuras)
hoje = timezone.now().date()
DutySchedule.objects.filter(date__gt=hoje).delete()
print("Escalas futuras removidas.")

# Buscar os tipos de tarefas
try:
    matinal = DutyType.objects.get(name__icontains='Matinal')
    vespertina = DutyType.objects.get(name__icontains='Vespertina')
except DutyType.DoesNotExist:
    # Se não existirem, criar os tipos
    print("Tipos de tarefa não encontrados, criando-os agora...")
    matinal = DutyType.objects.create(
        name="Reabastecimento Matinal",
        time="07:00:00",
        description="Limpeza e abastecimento matinal da máquina de café"
    )
    vespertina = DutyType.objects.create(
        name="Limpeza Vespertina",
        time="17:30:00",
        description="Limpeza e desligamento da máquina de café ao final do expediente"
    )
    print("Tipos de tarefa criados com sucesso!")

# Verificar e criar membros da equipe se necessário
membros = {
    'Juliano': {'email': 'juliano@empresa.com', 'phone': ''},
    'Wesley': {'email': 'wesley@empresa.com', 'phone': ''},
    'Ranielle': {'email': 'ranielle@empresa.com', 'phone': ''},
    'Guilherme - Mamada': {'email': 'mamada@empresa.com', 'phone': ''},
    'Guilherme - Monark': {'email': 'monark@empresa.com', 'phone': ''},
    'Allan - Cabelin': {'email': 'cabelin@empresa.com', 'phone': ''},
    'Leonardo': {'email': 'leonardo.dinizolv@gmail.com', 'phone': ''},
    'Gabriel': {'email': 'gabrielcesar48@gmail.com', 'phone': '35988656135'}
}

# Buscar ou criar membros
for nome, info in membros.items():
    membro, criado = TeamMember.objects.update_or_create(
        name=nome,
        defaults={
            'email': info['email'],
            'phone': info['phone'],
            'is_active': True
        }
    )
    if criado:
        print(f"Membro criado: {nome}")
    else:
        print(f"Membro atualizado: {nome}")

# Buscar os membros agora que garantimos que existem
juliano = TeamMember.objects.get(name='Juliano')
wesley = TeamMember.objects.get(name='Wesley')
ranielle = TeamMember.objects.get(name='Ranielle')
mamada = TeamMember.objects.get(name='Guilherme - Mamada')
monark = TeamMember.objects.get(name='Guilherme - Monark')
cabelin = TeamMember.objects.get(name='Allan - Cabelin')
leonardo = TeamMember.objects.get(name='Leonardo')
gabriel = TeamMember.objects.get(name='Gabriel')

# Função auxiliar para criar uma data
def criar_data(dia, mes, ano=2025):
    return date(ano, mes, dia)

# Cronograma conforme a tabela
cronograma = [
    # Data, Membro Inicial, Membro Final
    # Registros passados - já ocorreram
    (criar_data(13, 5), wesley, ranielle),
    
    # Registros futuros
    (criar_data(14, 5), monark, gabriel),
    (criar_data(15, 5), wesley, cabelin),
    (criar_data(16, 5), monark, leonardo),
    (criar_data(19, 5), wesley, mamada),
    (criar_data(20, 5), cabelin, ranielle),
    (criar_data(21, 5), monark, gabriel),
    (criar_data(22, 5), wesley, cabelin),
    (criar_data(23, 5), mamada, leonardo),
    (criar_data(26, 5), monark, ranielle),
    (criar_data(27, 5), wesley, gabriel),
    (criar_data(28, 5), cabelin, mamada),
    (criar_data(29, 5), mamada, gabriel),
    (criar_data(30, 5), leonardo, ranielle),
    (criar_data(2, 6), wesley, juliano),  # Juliano já está cadastrado
    (criar_data(3, 6), monark, cabelin),
    (criar_data(4, 6), cabelin, leonardo),
    (criar_data(5, 6), mamada, gabriel),
]

# Inserir registros no banco de dados
registros_criados = 0
registros_atualizados = 0

for data, membro_inicial, membro_final in cronograma:
    # Tarefa matinal (inicial)
    schedule, created = DutySchedule.objects.update_or_create(
        date=data, 
        duty_type=matinal,
        defaults={
            'member': membro_inicial,
            'completed': data < timezone.now().date()  # Marcar automaticamente como concluído se a data já passou
        }
    )
    
    if created:
        registros_criados += 1
    else:
        registros_atualizados += 1
    
    # Tarefa vespertina (final)
    schedule, created = DutySchedule.objects.update_or_create(
        date=data, 
        duty_type=vespertina,
        defaults={
            'member': membro_final,
            'completed': data < timezone.now().date()  # Marcar automaticamente como concluído se a data já passou
        }
    )
        
    if created:
        registros_criados += 1
    else:
        registros_atualizados += 1

print(f"Cronograma inserido com sucesso! {registros_criados} novos registros criados e {registros_atualizados} registros atualizados.")
print("Acesse a página inicial para verificar o cronograma.")