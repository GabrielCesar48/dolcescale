import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dolcescale.settings')  # use o nome do seu projeto
django.setup()

from django.utils import timezone
from datetime import timedelta, date
from core.models import TeamMember, DutyType, DutySchedule, Holiday
import pytz

tz = pytz.timezone('America/Sao_Paulo')
hoje = timezone.now().date()

print("=== GERANDO CRONOGRAMA DE LIMPEZA ÚNICA ===")

# Apagar escalas futuras
DutySchedule.objects.filter(date__gte=hoje).delete()
print("Escalas futuras removidas.")

# Criar ou resetar tipo de limpeza única (17:30)
DutyType.objects.filter(name__icontains='Limpeza Completa').delete()
tipo_limpeza = DutyType.objects.create(
    name="Limpeza Completa - 17:30",
    time="17:30:00",
    description="Limpeza completa da máquina de café para quem sai às 18:00"
)
print("Tipo de tarefa criado:", tipo_limpeza)

# Ordem da rotação fixa
usernames_rotacao = ['gabriel', 'allan', 'leonardo', 'mamada', 'ranielle', 'juliano', 'wesley']
membros_rotacao = []

for username in usernames_rotacao:
    try:
        membro = TeamMember.objects.get(user__username=username, is_active=True)
        membros_rotacao.append(membro)
        print(f"✓ {membro} incluído na rotação")
    except TeamMember.DoesNotExist:
        print(f"⚠️ Membro '{username}' não encontrado ou inativo.")

if not membros_rotacao:
    print("❌ Nenhum membro válido encontrado para gerar cronograma.")
    exit()

# Loop de criação de escalas
dias_uteis_gerados = 0
membro_index = 0
cronograma = []

data_atual = hoje
dias_alvo = 30

while dias_uteis_gerados < dias_alvo:
    # Pular finais de semana
    if data_atual.weekday() >= 5:
        data_atual += timedelta(days=1)
        continue

    # Pular feriados
    if Holiday.objects.filter(date=data_atual).exists():
        print(f"🎉 {data_atual} é feriado, pulando.")
        data_atual += timedelta(days=1)
        continue

    # Escolher membro respeitando restrição de sexta-feira para Gabriel
    tentativa = 0
    while True:
        membro = membros_rotacao[membro_index % len(membros_rotacao)]
        if data_atual.weekday() == 4 and membro.user.username == 'gabriel':
            membro_index += 1
            tentativa += 1
            if tentativa > len(membros_rotacao):
                print(f"❌ Nenhum membro disponível para {data_atual} (sexta-feira com restrição). Pulando.")
                data_atual += timedelta(days=1)
                continue
        else:
            break

    # Criar a escala
    schedule, created = DutySchedule.objects.update_or_create(
        date=data_atual,
        duty_type=tipo_limpeza,
        defaults={
            'member': membro,
            'completed': False,
            'notification_sent': False
        }
    )

    status = "✓ Criado" if created else "↻ Atualizado"
    print(f"{status}: {data_atual.strftime('%d/%m (%A)')} - {membro}")

    cronograma.append((data_atual, membro))
    membro_index += 1
    dias_uteis_gerados += 1
    data_atual += timedelta(days=1)

# Resumo
print("\n=== RESUMO ===")
print(f"Total de dias úteis agendados: {dias_uteis_gerados}")
print(f"Membros na rotação: {[m.user.username for m in membros_rotacao]}")
print("Primeiros 5 dias agendados:")
for data, membro in cronograma[:5]:
    print(f" - {data.strftime('%d/%m (%A)')} → {membro}")
