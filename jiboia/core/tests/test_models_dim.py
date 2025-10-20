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
    FactIssue,
    FactProjectSnapshot,
)


@pytest.mark.django_db
def test_dim_projeto_creation():
    """Testa criação de dimensão projeto"""
    projeto = DimProjeto.objects.create(
        id_project_jiba=1001,
        id_project_jira=2001,
        project_name="Projeto Alpha",
        start_date=date(2025, 1, 15),
        end_date=date(2026, 1, 15),
    )

    assert projeto.id_project_jiba == 1001
    assert projeto.id_project_jira == 2001
    assert projeto.project_name == "Projeto Alpha"
    assert projeto.start_date == date(2025, 1, 15)
    assert projeto.end_date == date(2026, 1, 15)


@pytest.mark.django_db
def test_dim_dev_creation():
    """Testa criação de dimensão desenvolvedor"""
    user = get_user_model().objects.create_user(username="dev1", password="test123")

    dev = DimDev.objects.create(
        id_dev_jiba=user.id,
        id_dev_jira=1001,  # Este valor precisa estar presente
        dev_name=user.username,
        valor_hora=50.0,
    )

    assert dev.id_dev_jiba == user.id
    assert dev.id_dev_jira == 1001
    assert dev.dev_name == "dev1"
    assert dev.valor_hora == 50.0


@pytest.mark.django_db
def test_dim_intervalo_temporal_creation_and_duration():
    """Testa criação de dimensão temporal e cálculo de duração"""
    start_date = timezone.make_aware(datetime(2025, 10, 1, 9, 0))
    end_date = timezone.make_aware(datetime(2025, 10, 1, 17, 30))

    intervalo = DimIntervaloTemporal.objects.create(
        granularity_type=DimIntervaloTemporal.TipoGranularidade.DIA, start_date=start_date, end_date=end_date
    )

    assert intervalo.granularity_type == "DIA"
    assert intervalo.duracao_total_minutos == 510


@pytest.mark.django_db
def test_dim_status_creation():
    """Testa criação de dimensão status"""
    status = DimStatus.objects.create(id_status_jira=1, id_status_jiba=101, status_name="Concluído")

    assert status.id_status_jira == 1
    assert status.id_status_jiba == 101
    assert status.status_name == "Concluído"


@pytest.mark.django_db
def test_dim_issue_type_creation():
    """Testa criação de dimensão tipo de issue"""
    tipo = DimTipoIssue.objects.create(id_type_jira=1, id_type_jiba=201, name_type="Task")

    assert tipo.id_type_jira == 1
    assert tipo.id_type_jiba == 201
    assert tipo.name_type == "Task"


@pytest.mark.django_db
def test_fato_issue_creation_with_relationships():
    dimprojeto = DimProjeto.objects.create(
        id_project_jiba=1001,
        id_project_jira=2001,
        project_name="Projeto Alpha",
        start_date=date(2025, 1, 15),
    )

    status = DimStatus.objects.create(id_status_jira=1, id_status_jiba=101, status_name="Concluído")

    tipo = DimTipoIssue.objects.create(id_type_jira=1, id_type_jiba=201, name_type="Task")

    intervalo = DimIntervaloTemporal.objects.create(
        granularity_type=DimIntervaloTemporal.TipoGranularidade.DIA,
        start_date=timezone.now(),
        end_date=timezone.now(),
    )

    fato = FactIssue.objects.create(
        project=dimprojeto, status=status, issue_type=tipo, worklog_interval=intervalo, total_issue=20
    )

    assert fato.project == dimprojeto
    assert fato.status == status
    assert fato.issue_type == tipo
    assert fato.worklog_interval.duracao_total_minutos == 0


@pytest.mark.django_db
def test_fato_issue_calculated_properties():
    projeto = DimProjeto.objects.create(
        id_project_jiba=1001,
        id_project_jira=2001,
        project_name="Projeto Alpha",
        start_date=date(2025, 1, 15),
    )

    status = DimStatus.objects.create(id_status_jira=1, id_status_jiba=101, status_name="Concluído")

    tipo = DimTipoIssue.objects.create(id_type_jira=1, id_type_jiba=201, name_type="Task")

    intervalo = DimIntervaloTemporal.objects.create(
        granularity_type=DimIntervaloTemporal.TipoGranularidade.DIA,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(hours=2),
    )

    fato = FactIssue.objects.create(
        project=projeto, status=status, issue_type=tipo, worklog_interval=intervalo, total_issue=200
    )

    assert fato.total_issue == 200


@pytest.mark.django_db
@freeze_time("2025-10-15")
def test_fato_projeto_snapshot_creation_and_properties():
    """Testa criação do snapshot de projeto e propriedades calculadas"""
    projeto = DimProjeto.objects.create(
        id_project_jiba=1001,
        id_project_jira=2001,
        project_name="Projeto Alpha",
        start_date=date(2025, 1, 15),
        end_date=date(2026, 12, 31),
    )

    intervalo = DimIntervaloTemporal.objects.create(
        granularity_type=DimIntervaloTemporal.TipoGranularidade.DIA,
        start_date=timezone.make_aware(datetime(2025, 10, 15, 0, 0)),
        end_date=timezone.make_aware(datetime(2025, 10, 15, 23, 59)),
    )

    snapshot = FactProjectSnapshot.objects.create(
        project=projeto,
        snapshot_interval=intervalo,
        projection_end_days=77,
        current_project_cost_rs=25000.0,
        total_accumulated_minutes=12000,
    )

    assert snapshot.project == projeto
    assert snapshot.current_project_cost_rs == 25000
    assert snapshot.total_accumulated_minutes == 12000
    assert snapshot.minutes_left_end_project > 70


@pytest.mark.django_db
def test_fato_projeto_snapshot_with_multiple_snapshots():
    """Testa múltiplos snapshots para o mesmo projeto"""
    projeto = DimProjeto.objects.create(
        id_project_jiba=1001,
        id_project_jira=2001,
        project_name="Projeto Alpha",
        start_date=date(2025, 1, 15),
        end_date=date(2025, 12, 31),
    )

    intervalo1 = DimIntervaloTemporal.objects.create(
        granularity_type=DimIntervaloTemporal.TipoGranularidade.DIA,
        start_date=timezone.make_aware(datetime(2025, 10, 1, 0, 0)),
        end_date=timezone.make_aware(datetime(2025, 10, 1, 23, 59)),
    )

    FactProjectSnapshot.objects.create(
        project=projeto,
        snapshot_interval=intervalo1,
        projection_end_days=100,
        current_project_cost_rs=15000.0,
        total_accumulated_minutes=8000,
    )

    intervalo2 = DimIntervaloTemporal.objects.create(
        granularity_type=DimIntervaloTemporal.TipoGranularidade.DIA,
        start_date=timezone.make_aware(datetime(2025, 10, 2, 0, 0)),
        end_date=timezone.make_aware(datetime(2025, 10, 2, 23, 59)),
    )

    FactProjectSnapshot.objects.create(
        project=projeto,
        snapshot_interval=intervalo2,
        projection_end_days=77,
        current_project_cost_rs=18000.0,
        total_accumulated_minutes=9500,
    )

    snapshots = FactProjectSnapshot.objects.filter(project=projeto).order_by("snapshot_interval__start_date")

    assert snapshots.count() == 2
    assert snapshots[0].projection_end_days == 100
    assert snapshots[1].projection_end_days == 77

    assert snapshots[1].total_accumulated_minutes > snapshots[0].total_accumulated_minutes


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
            granularity_type=tipo, start_date=timezone.now(), end_date=timezone.now()
        )
        assert intervalo.granularity_type == tipo

    assert DimIntervaloTemporal.objects.count() == 6


@pytest.mark.django_db
def test_dimensional_models_string_representation():
    """Testa representação string dos modelos dimensionais"""
    user = get_user_model().objects.create_user(username="dev1", password="test123")

    projeto = DimProjeto.objects.create(
        id_project_jiba=1001,
        id_project_jira=2001,
        project_name="Projeto Alpha",
        start_date=date(2025, 1, 15),
        end_date=date(2025, 12, 31),
    )

    dev = DimDev.objects.create(id_dev_jiba=user.id, id_dev_jira=1001, dev_name=user.username, valor_hora=50.0)

    status = DimStatus.objects.create(id_status_jira=1, id_status_jiba=101, status_name="Concluído")

    tipo = DimTipoIssue.objects.create(id_type_jira=1, id_type_jiba=201, name_type="Task")

    assert str(projeto) == "Projeto Alpha"
    assert str(dev.dev_name) == "dev1"
    assert str(status) == "Concluído"
    assert str(tipo) == "Task"
