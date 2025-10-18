from datetime import date, datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from freezegun import freeze_time

from jiboia.core.models import (
    DimDev,
    DimIntervaloTemporal,
    DimProjeto,
    DimStatus,
    DimTipoIssue,
    FatoIssue,
    FatoProjetoSnapshot,
)


@pytest.mark.django_db
def test_dim_projeto_creation():
    """Testa criação de dimensão projeto"""
    projeto = DimProjeto.objects.create(
        id_projeto_jiba=1001,
        id_projeto_jira=2001,
        nome_projeto="Projeto Alpha",
        data_inicio=date(2025, 1, 15),
        data_fim=date(2025, 12, 31),
    )

    assert projeto.id_projeto_jiba == 1001
    assert projeto.id_projeto_jira == 2001
    assert projeto.nome_projeto == "Projeto Alpha"
    assert projeto.data_inicio == date(2025, 1, 15)
    assert projeto.data_fim == date(2025, 12, 31)


@pytest.mark.django_db
def test_dim_dev_creation():
    """Testa criação de dimensão desenvolvedor"""
    user = get_user_model().objects.create_user(username="dev1", password="test123")

    dev = DimDev.objects.create(
        id_dev_jiba=user.id,
        id_dev_jira=1001,  # Este valor precisa estar presente
        nome_dev=user.username,
        valor_hora=50.0,
    )

    assert dev.id_dev_jiba == user.id
    assert dev.id_dev_jira == 1001
    assert dev.nome_dev == "dev1"
    assert dev.valor_hora == 50.0


@pytest.mark.django_db
def test_dim_intervalo_temporal_creation_and_duration():
    """Testa criação de dimensão temporal e cálculo de duração"""
    data_inicio = timezone.make_aware(datetime(2025, 10, 1, 9, 0))
    data_fim = timezone.make_aware(datetime(2025, 10, 1, 17, 30))

    intervalo = DimIntervaloTemporal.objects.create(
        tipo_granularidade=DimIntervaloTemporal.TipoGranularidade.DIA, data_inicio=data_inicio, data_fim=data_fim
    )

    assert intervalo.tipo_granularidade == "DIA"
    assert intervalo.duracao_total_minutos == 510


@pytest.mark.django_db
def test_dim_status_creation():
    """Testa criação de dimensão status"""
    status = DimStatus.objects.create(id_status_jira=1, id_status_jiba=101, nome_status="Concluído")

    assert status.id_status_jira == 1
    assert status.id_status_jiba == 101
    assert status.nome_status == "Concluído"


@pytest.mark.django_db
def test_dim_tipo_issue_creation():
    """Testa criação de dimensão tipo de issue"""
    tipo = DimTipoIssue.objects.create(id_tipo_jira=1, id_tipo_jiba=201, nome_tipo="Task")

    assert tipo.id_tipo_jira == 1
    assert tipo.id_tipo_jiba == 201
    assert tipo.nome_tipo == "Task"


@pytest.mark.django_db
def test_fato_issue_creation_with_relationships():
    """Testa criação de fato issue com relacionamentos"""
    # Criar dimensões
    user = get_user_model().objects.create_user(username="dev1", password="test123")

    projeto = DimProjeto.objects.create(
        id_projeto_jiba=1001,
        id_projeto_jira=2001,
        nome_projeto="Projeto Alpha",
        data_inicio=date(2025, 1, 15),
        data_fim=date(2025, 12, 31),
    )

    dev = DimDev.objects.create(id_dev_jiba=user.id, id_dev_jira=1001, nome_dev=user.username, valor_hora=50.0)

    status = DimStatus.objects.create(id_status_jira=1, id_status_jiba=101, nome_status="Concluído")

    tipo = DimTipoIssue.objects.create(id_tipo_jira=1, id_tipo_jiba=201, nome_tipo="Task")

    intervalo = DimIntervaloTemporal.objects.create(
        tipo_granularidade=DimIntervaloTemporal.TipoGranularidade.DIA,
        data_inicio=timezone.now(),
        data_fim=timezone.now(),
    )

    fato = FatoIssue.objects.create(
        id_issue_jira=3001,
        data_criacao=timezone.now(),
        id_issue_jiba=4001,
        projeto=projeto,
        dev=dev,
        status=status,
        tipo_issue=tipo,
        intervalo_trabalho=intervalo,
    )

    assert fato.id_issue_jira == 3001
    assert fato.id_issue_jiba == 4001
    assert fato.projeto == projeto
    assert fato.dev == dev
    assert fato.status == status
    assert fato.tipo_issue == tipo
    assert fato.intervalo_trabalho.duracao_total_minutos == 0


@pytest.mark.django_db
def test_fato_issue_calculated_properties():
    """Testa propriedades calculadas do fato issue"""
    user = get_user_model().objects.create_user(username="dev1", password="test123")

    projeto = DimProjeto.objects.create(
        id_projeto_jiba=1001,
        id_projeto_jira=2001,
        nome_projeto="Projeto Alpha",
        data_inicio=date(2025, 1, 15),
        data_fim=date(2025, 12, 31),
    )

    dev = DimDev.objects.create(id_dev_jiba=user.id, id_dev_jira=1001, nome_dev=user.username, valor_hora=50.0)

    status = DimStatus.objects.create(id_status_jira=1, id_status_jiba=101, nome_status="Concluído")

    tipo = DimTipoIssue.objects.create(id_tipo_jira=1, id_tipo_jiba=201, nome_tipo="Task")

    intervalo = DimIntervaloTemporal.objects.create(
        tipo_granularidade=DimIntervaloTemporal.TipoGranularidade.DIA,
        data_inicio=timezone.now(),
        data_fim=timezone.now() + timedelta(hours=2),
    )

    fato = FatoIssue.objects.create(
        id_issue_jira=3001,
        id_issue_jiba=4001,
        projeto=projeto,
        dev=dev,
        status=status,
        tipo_issue=tipo,
        data_criacao=timezone.now(),
        intervalo_trabalho=intervalo,
    )

    assert fato.minutos_gastos == 120


@pytest.mark.django_db
@freeze_time("2025-10-15")
def test_fato_projeto_snapshot_creation_and_properties():
    """Testa criação do snapshot de projeto e propriedades calculadas"""
    projeto = DimProjeto.objects.create(
        id_projeto_jiba=1001,
        id_projeto_jira=2001,
        nome_projeto="Projeto Alpha",
        data_inicio=date(2025, 1, 15),
        data_fim=date(2025, 12, 31),
    )

    intervalo = DimIntervaloTemporal.objects.create(
        tipo_granularidade=DimIntervaloTemporal.TipoGranularidade.DIA,
        data_inicio=timezone.make_aware(datetime(2025, 10, 15, 0, 0)),
        data_fim=timezone.make_aware(datetime(2025, 10, 15, 23, 59)),
    )

    snapshot = FatoProjetoSnapshot.objects.create(
        projeto=projeto,
        intervalo_snapshot=intervalo,
        versao_carga=timezone.now(),
        projecao_termino_dias=77,
        total_issues=15,
        custo_do_projeto_atual_rs=25000.0,
        total_horas_acumuladas=12000,
    )

    assert snapshot.projeto == projeto
    assert snapshot.total_issues == 15
    assert snapshot.custo_do_projeto_atual_rs == 25000
    assert snapshot.tota_minutos_acumulados == 12000

    assert snapshot.minutos_faltando_fim_projeto > 70


@pytest.mark.django_db
def test_fato_projeto_snapshot_with_multiple_snapshots():
    """Testa múltiplos snapshots para o mesmo projeto"""
    projeto = DimProjeto.objects.create(
        id_projeto_jiba=1001,
        id_projeto_jira=2001,
        nome_projeto="Projeto Alpha",
        data_inicio=date(2025, 1, 15),
        data_fim=date(2025, 12, 31),
    )

    intervalo1 = DimIntervaloTemporal.objects.create(
        tipo_granularidade=DimIntervaloTemporal.TipoGranularidade.DIA,
        data_inicio=timezone.make_aware(datetime(2025, 10, 1, 0, 0)),
        data_fim=timezone.make_aware(datetime(2025, 10, 1, 23, 59)),
    )

    FatoProjetoSnapshot.objects.create(
        projeto=projeto,
        intervalo_snapshot=intervalo1,
        versao_carga=timezone.now(),
        projecao_termino_dias=77,
        total_issues=10,
        custo_do_projeto_atual_rs=15000.0,
        total_horas_acumuladas=8000,
    )

    intervalo2 = DimIntervaloTemporal.objects.create(
        tipo_granularidade=DimIntervaloTemporal.TipoGranularidade.DIA,
        data_inicio=timezone.make_aware(datetime(2025, 10, 2, 0, 0)),
        data_fim=timezone.make_aware(datetime(2025, 10, 2, 23, 59)),
    )

    FatoProjetoSnapshot.objects.create(
        projeto=projeto,
        intervalo_snapshot=intervalo2,
        versao_carga=timezone.now(),
        projecao_termino_dias=77,
        total_issues=12,
        custo_do_projeto_atual_rs=18000.0,
        total_horas_acumuladas=9500,
    )

    snapshots = FatoProjetoSnapshot.objects.filter(projeto=projeto).order_by("intervalo_snapshot__data_inicio")

    assert snapshots.count() == 2
    assert snapshots[0].total_issues == 10
    assert snapshots[1].total_issues == 12

    assert snapshots[1].custo_do_projeto_atual_rs > snapshots[0].custo_do_projeto_atual_rs


@pytest.mark.django_db
def test_dim_intervalo_temporal_granularidade_choices():
    """Testa as opções de granularidade do intervalo temporal"""
    tipos = [
        DimIntervaloTemporal.TipoGranularidade.DIA,
        DimIntervaloTemporal.TipoGranularidade.SEMANA,
        DimIntervaloTemporal.TipoGranularidade.MES,
        DimIntervaloTemporal.TipoGranularidade.TRIMESTRE,
        DimIntervaloTemporal.TipoGranularidade.SEMESTRE,
        DimIntervaloTemporal.TipoGranularidade.ANO,
    ]

    for tipo in tipos:
        intervalo = DimIntervaloTemporal.objects.create(
            tipo_granularidade=tipo, data_inicio=timezone.now(), data_fim=timezone.now()
        )
        assert intervalo.tipo_granularidade == tipo

    assert DimIntervaloTemporal.objects.count() == 6


@pytest.mark.django_db
def test_dimensional_models_string_representation():
    """Testa representação string dos modelos dimensionais"""
    user = get_user_model().objects.create_user(username="dev1", password="test123")

    projeto = DimProjeto.objects.create(
        id_projeto_jiba=1001,
        id_projeto_jira=2001,
        nome_projeto="Projeto Alpha",
        data_inicio=date(2025, 1, 15),
        data_fim=date(2025, 12, 31),
    )

    dev = DimDev.objects.create(id_dev_jiba=user.id, id_dev_jira=1001, nome_dev=user.username, valor_hora=50.0)

    status = DimStatus.objects.create(id_status_jira=1, id_status_jiba=101, nome_status="Concluído")

    tipo = DimTipoIssue.objects.create(id_tipo_jira=1, id_tipo_jiba=201, nome_tipo="Task")

    assert str(projeto) == "Projeto Alpha"
    assert str(dev) == "Dev 4"
    assert str(status) == "Concluído"
    assert str(tipo) == "Task"
