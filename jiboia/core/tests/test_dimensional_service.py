from datetime import date, datetime, timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone
from freezegun import freeze_time

from jiboia.accounts.models import User
from jiboia.core.models import (
    DimDev,
    DimIssue,
    DimProjeto,
    DimStatus,
    DimTipoIssue,
    FactEsforco,
    FactIssue,
    FactProjectSnapshot,
    Issue,
    IssueType,
    Project,
    StatusType,
    TimeLog,
)
from jiboia.core.service.dimensional_svc import (
    DimDevService,
    DimensionalService,
    DimIntervaloTemporalService,
    DimIssueService,
    DimIssueTypesService,
    DimProjetoService,
    DimStatusTypeService,
    TipoGranularidade,
)


@pytest.mark.django_db
def test_generate_project_snapshot_data_creates_snapshots():
    projeto = Project.objects.create(
        key="PRJ1",
        name="Projeto Teste",
        description="Desc",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="uuid1",
        jira_id=1,
        projectTypeKey="software",
    )
    issue = Issue.objects.create(
        description="Issue 1", created_at=timezone.now(), project=projeto, time_estimate_seconds=3600, jira_id=2020
    )
    TimeLog.objects.create(id_issue=issue, seconds=1800, log_date=timezone.now(), jira_id=issue.id)

    intervalo_tempo = DimIntervaloTemporalService(TipoGranularidade.DIA)
    DimensionalService.generate_project_snapshot_data(intervalo_tempo)

    assert FactProjectSnapshot.objects.count() == 1
    snap = FactProjectSnapshot.objects.first()
    assert snap.project.project_name == "Projeto Teste"
    assert snap.snapshot_interval.granularity_type == TipoGranularidade.DIA.value
    assert snap.current_project_cost_rs >= 0
    assert snap.total_accumulated_minutes >= 0


@pytest.mark.django_db
def test_generate_project_snapshot_data_multiple_projects():
    projeto1 = Project.objects.create(
        key="PRJ1",
        name="Projeto 1",
        description="Desc",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="uuid1",
        jira_id=1,
        projectTypeKey="software",
    )
    projeto2 = Project.objects.create(
        key="PRJ2",
        name="Projeto 2",
        description="Desc",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="uuid2",
        jira_id=2,
        projectTypeKey="software",
    )
    Issue.objects.create(description="Issue 1", created_at=timezone.now(), project=projeto1, time_estimate_seconds=3600)
    Issue.objects.create(description="Issue 2", created_at=timezone.now(), project=projeto2, time_estimate_seconds=7200)
    intervalo_tempo = DimIntervaloTemporalService(TipoGranularidade.DIA)
    DimensionalService.generate_project_snapshot_data(intervalo_tempo)
    assert FactProjectSnapshot.objects.count() == 2
    nomes = set(FactProjectSnapshot.objects.values_list("project__project_name", flat=True))
    assert "Projeto 1" in nomes
    assert "Projeto 2" in nomes


@pytest.mark.django_db(reset_sequences=True)
def test_load_fato_issue():
    issue_type_bug = IssueType.objects.create(name="Bug", description="Bug Issue", subtask=False, jira_id=101)
    issue_type_history = IssueType.objects.create(
        name="History", description="History Issue", subtask=False, jira_id=102
    )
    status_type_open = StatusType.objects.create(name="Open", key="op", jira_id=201)
    status_type_done = StatusType.objects.create(name="Done", key="dn", jira_id=200)
    projeto = Project.objects.create(
        key="yyy",
        name="Um projeto qualquer",
        description="Desc",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="uid",
        jira_id=141414,
        projectTypeKey="software",
    )
    Project.objects.create(
        key="PPP",
        name="Outro projeto qualquer",
        description="Desc",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="uuid22",
        jira_id=151515,
        projectTypeKey="software",
    )
    Issue.objects.create(
        description="Issue projeto teste",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=1111,
        type_issue=issue_type_history,
        status=status_type_open,
    )
    Issue.objects.create(
        description="Issue projeto OUTRO",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2222,
        type_issue=issue_type_history,
        status=status_type_open,
    )
    Issue.objects.create(
        description="Issue projeto outro de outro",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=3333,
        type_issue=issue_type_bug,
        status=status_type_done,
    )
    Issue.objects.create(
        description="Issue projeto mais outros",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=4444,
        type_issue=issue_type_bug,
        status=status_type_open,
    )
    Issue.objects.create(
        description="Issue projeto outrinho",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=5555,
        type_issue=issue_type_history,
        status=status_type_done,
    )
    intervalo_tempo = DimIntervaloTemporalService(TipoGranularidade.DIA)
    DimensionalService.generate_fact_issue(intervalo_tempo)
    assert FactIssue.objects.count() == 8
    fato_bug_open = FactIssue.objects.filter(
        issue_type__name_type="Bug", status__status_name="Open", project__id=projeto.id
    )
    fato_bug_done = FactIssue.objects.filter(
        issue_type__name_type="Bug", status__status_name="Done", project__id=projeto.id
    )
    fato_history_open = FactIssue.objects.filter(
        issue_type__name_type="History", status__status_name="Open", project__id=projeto.id
    )
    fato_history_done = FactIssue.objects.filter(
        issue_type__name_type="History", status__status_name="Done", project__id=projeto.id
    )

    assert fato_bug_open.count() == 1
    assert fato_bug_open[0].total_issue == 1
    assert fato_bug_done.count() == 1
    assert fato_bug_done[0].total_issue == 1
    assert fato_history_open.count() == 1
    assert fato_history_open[0].total_issue == 2
    assert fato_history_done.count() == 1
    assert fato_history_done[0].total_issue == 1


@pytest.mark.django_db
def test_generate_fact_worlog():
    dev = User.objects.create_user(
        username="yan",
        first_name="Jon",
        last_name="Snow",
        email="jon@example.com",
        password="snow",
        valor_hora=60,
        jira_id=1,
    )
    dev2 = User.objects.create_user(
        username="jon2",
        first_name="Jon",
        last_name="Snow",
        email="jon2@example.com",
        password="snow",
        valor_hora=50,
        jira_id=2,
    )
    issue_type_bug = IssueType.objects.create(name="Bug", description="Bug Issue", subtask=False, jira_id=101)
    issue_type = DimTipoIssue.objects.create(
        id_type_jira=issue_type_bug.jira_id,
        id_type_jiba=issue_type_bug.id,
        name_type=issue_type_bug.name,
    )

    status_type_open = StatusType.objects.create(name="Open", key="op", jira_id=201)
    DimStatus.objects.create(
        id_status_jira=status_type_open.jira_id,
        id_status_jiba=status_type_open.id,
        status_name=status_type_open.name,
    )
    projeto = Project.objects.create(
        key="PRJ1",
        name="Projeto Teste",
        description="Desc",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="uuid1",
        jira_id=1,
        projectTypeKey="software",
    )
    project2 = DimProjeto.objects.create(
        id_project_jiba=projeto.id,
        id_project_jira=projeto.jira_id,
        start_date=projeto.start_date_project,
        project_name=projeto.name,
    )
    Project.objects.create(
        key="PPP",
        name="Projeto Teste",
        description="Desc",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="uuid2",
        jira_id=2,
        projectTypeKey="software",
    )
    issue1 = Issue.objects.create(
        description="Issue projeto teste",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2021,
        type_issue=issue_type_bug,
        status=status_type_open,
    )
    issue2 = Issue.objects.create(
        description="Issue projeto OUTRO",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2021,
        type_issue=issue_type_bug,
        status=status_type_open,
    )
    Issue.objects.create(
        description="Issue projeto teste",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2020,
        type_issue=issue_type_bug,
        status=status_type_open,
    )
    Issue.objects.create(
        description="Issue projeto teste",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2022,
        type_issue=issue_type_bug,
        status=status_type_open,
    )
    Issue.objects.create(
        description="Issue projeto teste",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2023,
        type_issue=issue_type_bug,
        status=status_type_open,
    )

    issues_fatos = Issue.objects.filter()
    for issue_fato in issues_fatos:
        DimIssue.objects.create(
            id_issue_jira=issue_fato.jira_id,
            id_issue_jiba=issue_fato.id,
            project=project2,
            issue_type=issue_type,
            start_date=issue_fato.start_date,
        )

    log_date = timezone.now()
    log_date_ontem = datetime(1999, 1, 1)
    TimeLog.objects.create(id_user=dev, id_issue=issue1, seconds=1200, log_date=log_date, jira_id=444)
    TimeLog.objects.create(id_user=dev, id_issue=issue2, seconds=2400, log_date=log_date, jira_id=555)
    timelog_alterado = TimeLog.objects.create(
        id_user=dev2, id_issue=issue1, seconds=10000, log_date=log_date_ontem, jira_id=666
    )
    timelog_alterado.log_date = log_date_ontem
    timelog_alterado.save()
    intervalo_tempo = DimIntervaloTemporalService(TipoGranularidade.DIA)
    success = DimensionalService.generate_fact_worklog(intervalo_tempo)

    assert success is True

    fato_dev1 = FactEsforco.objects.filter(dev__id_dev_jira=dev.jira_id)
    fato_dev2 = FactEsforco.objects.filter(dev__id_dev_jira=dev2.jira_id)

    assert len(FactEsforco.objects.all()) == 4
    assert len(fato_dev1) == 2
    assert len(fato_dev2) == 2
    assert fato_dev1[0].accumulated_minutes == 60
    assert fato_dev1[0].accumulated_cost == 60
    assert fato_dev1[1].accumulated_minutes == 0
    assert fato_dev1[1].accumulated_cost == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "granularity, refer, expected_start, expected_end",
    [
        (
            TipoGranularidade.DIA,
            datetime(2024, 10, 20, 12, 0),
            datetime(2024, 10, 20, 0, 0),
            datetime(2024, 10, 21, 0, 0),
        ),
        (
            TipoGranularidade.SEMANA,
            datetime(2024, 10, 17, 15, 0),  # quinta
            datetime(2024, 10, 14, 0, 0),  # segunda
            datetime(2024, 10, 21, 0, 0),
        ),
        (
            TipoGranularidade.MES,
            datetime(2024, 12, 10, 10, 0),
            datetime(2024, 12, 1, 0, 0),
            datetime(2025, 1, 1, 0, 0),
        ),
        (
            TipoGranularidade.TRIMESTRE,
            datetime(2024, 11, 5, 12, 0),
            datetime(2024, 10, 1, 0, 0),
            datetime(2025, 1, 1, 0, 0),
        ),
        (
            TipoGranularidade.SEMESTRE,
            datetime(2024, 8, 20, 10, 0),
            datetime(2024, 7, 1, 0, 0),
            datetime(2025, 1, 1, 0, 0),
        ),
        (
            TipoGranularidade.ANO,
            datetime(2024, 6, 15, 14, 0),
            datetime(2024, 1, 1, 0, 0),
            datetime(2025, 1, 1, 0, 0),
        ),
    ],
)
def test_dim_intervalo_temporal_service(granularity, refer, expected_start, expected_end):
    service = DimIntervaloTemporalService(granularity)
    start, end = service.create_interval(granularity, refer)

    assert start == expected_start
    assert end == expected_end

    dim = service.dimtemporal
    assert dim.granularity_type == service.granularity_type.value
    assert dim.start_date == service.start_date
    assert dim.end_date == service.end_date


@pytest.mark.django_db
def test_dim_dev_service_create_devs():
    """Testa a criação de desenvolvedores dimensionais"""
    # Setup
    dev1 = User.objects.create_user(
        username="dev1",
        first_name="João",
        last_name="Silva",
        email="joao@example.com",
        password="pass123",
        valor_hora=75.0,
        jira_id=100,
    )
    dev2 = User.objects.create_user(
        username="dev2",
        first_name="Maria",
        last_name="Santos",
        email="maria@example.com",
        password="pass123",
        valor_hora=80.0,
        jira_id=200,
    )

    # Criar TimeLogs para que os devs sejam incluídos
    project = Project.objects.create(
        key="TEST",
        name="Test Project",
        description="Test",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="test-uuid",
        jira_id=999,
        projectTypeKey="software",
    )
    issue = Issue.objects.create(
        description="Test Issue",
        project=project,
        time_estimate_seconds=3600,
        jira_id=888,
    )

    hoje = timezone.now()
    TimeLog.objects.create(id_user=dev1, id_issue=issue, seconds=1800, log_date=hoje, jira_id=111)
    TimeLog.objects.create(id_user=dev2, id_issue=issue, seconds=2400, log_date=hoje, jira_id=222)

    # Execute
    dim_dev_service = DimDevService()

    # Assert
    assert len(dim_dev_service.devs) == 2

    # Verificar se DimDev foram criados
    dim_devs = DimDev.objects.all()
    assert dim_devs.count() == 2

    # Verificar dados específicos
    dim_dev1 = DimDev.objects.get(id_dev_jira=100)
    assert dim_dev1.dev_name == "dev1"
    assert dim_dev1.valor_hora == 75.0

    dim_dev2 = DimDev.objects.get(id_dev_jira=200)
    assert dim_dev2.dev_name == "dev2"
    assert dim_dev2.valor_hora == 80.0


@pytest.mark.django_db
def test_dim_dev_service_update_existing():
    """Testa atualização de desenvolvedor existente"""
    # Setup - criar dev e DimDev inicial
    dev = User.objects.create_user(
        username="dev_test",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password="pass123",
        valor_hora=50.0,
        jira_id=300,
    )
    DimDev.objects.create(
        id_dev_jiba=dev.id,
        id_dev_jira=dev.jira_id,
        dev_name="old_username",
        valor_hora=40.0,
    )

    # Criar TimeLog para incluir o dev no serviço
    project = Project.objects.create(
        key="UPD",
        name="Update Project",
        description="Test",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="upd-uuid",
        jira_id=777,
        projectTypeKey="software",
    )
    issue = Issue.objects.create(
        description="Update Issue",
        project=project,
        time_estimate_seconds=3600,
        jira_id=666,
    )
    TimeLog.objects.create(id_user=dev, id_issue=issue, seconds=1200, log_date=timezone.now(), jira_id=333)

    # Execute
    DimDevService()

    # Assert
    dim_dev_atualizado = DimDev.objects.get(id_dev_jira=300)
    assert dim_dev_atualizado.dev_name == "dev_test"  # Deve ter sido atualizado
    assert dim_dev_atualizado.valor_hora == 50.0  # Deve ter sido atualizado
    assert DimDev.objects.count() == 1  # Não deve duplicar


@pytest.mark.django_db
def test_dim_projeto_service():
    """Testa o serviço de projetos dimensionais"""
    # Setup
    projeto1 = Project.objects.create(
        key="PROJ1",
        name="Projeto Alpha",
        description="Descrição Alpha",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date() + timedelta(days=30),
        uuid="alpha-uuid",
        jira_id=1001,
        projectTypeKey="software",
    )
    Project.objects.create(
        key="PROJ2",
        name="Projeto Beta",
        description="Descrição Beta",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date() + timedelta(days=60),
        uuid="beta-uuid",
        jira_id=1002,
        projectTypeKey="business",
    )
    intervalo_tempo_dia = DimIntervaloTemporalService(TipoGranularidade.DIA)
    service = DimProjetoService(intervalo_tempo_dia)
    assert len(service.projetos_filtros) == 2
    dim_projetos = DimProjeto.objects.all()
    assert dim_projetos.count() == 2
    dim_proj1 = DimProjeto.objects.get(id_project_jira=1001)
    assert dim_proj1.project_name == "Projeto Alpha"
    assert dim_proj1.start_date == projeto1.start_date_project
    dim_proj2 = DimProjeto.objects.get(id_project_jira=1002)
    assert dim_proj2.project_name == "Projeto Beta"


@pytest.mark.django_db
def test_dim_issue_types_service():
    """Testa o serviço de tipos de issue dimensionais"""
    # Setup
    IssueType.objects.create(name="Bug", description="Bug issues", subtask=False, jira_id=10001)
    IssueType.objects.create(name="Story", description="User stories", subtask=False, jira_id=10002)
    IssueType.objects.create(name="Task", description="General tasks", subtask=True, jira_id=10003)

    # Execute
    service = DimIssueTypesService()

    # Assert
    assert len(service.issues_types) == 3

    # Verificar se DimTipoIssue foram criados
    dim_types = DimTipoIssue.objects.all()
    assert dim_types.count() == 3

    # Verificar dados específicos
    dim_bug = DimTipoIssue.objects.get(id_type_jira=10001)
    assert dim_bug.name_type == "Bug"

    dim_story = DimTipoIssue.objects.get(id_type_jira=10002)
    assert dim_story.name_type == "Story"

    dim_task = DimTipoIssue.objects.get(id_type_jira=10003)
    assert dim_task.name_type == "Task"


@pytest.mark.django_db
def test_dim_status_type_service():
    """Testa o serviço de status dimensionais"""
    StatusType.objects.create(name="Open", key="open", jira_id=20001)
    StatusType.objects.create(name="In Progress", key="progress", jira_id=20002)
    StatusType.objects.create(name="Done", key="done", jira_id=20003)

    service = DimStatusTypeService()

    # Assert
    assert len(service.status_types) == 3

    # Verificar se DimStatus foram criados
    dim_status_list = DimStatus.objects.all()
    assert dim_status_list.count() == 3

    # Verificar dados específicos
    dim_open = DimStatus.objects.get(id_status_jira=20001)
    assert dim_open.status_name == "Open"

    dim_progress = DimStatus.objects.get(id_status_jira=20002)
    assert dim_progress.status_name == "In Progress"

    dim_done = DimStatus.objects.get(id_status_jira=20003)
    assert dim_done.status_name == "Done"


@pytest.mark.django_db
def test_dim_issue_service_with_timelogs():
    """Testa o serviço de issues dimensionais com TimeLogs de hoje"""
    user = User.objects.create_user(
        username="test_user", email="user@test.com", password="pass123", valor_hora=60.0, jira_id=400
    )

    project = Project.objects.create(
        key="ISS",
        name="Issue Test Project",
        description="Test",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="iss-uuid",
        jira_id=2001,
        projectTypeKey="software",
    )

    issue_type = IssueType.objects.create(name="Feature", description="Feature requests", subtask=False, jira_id=30001)

    issue1 = Issue.objects.create(
        description="Issue with timeLog today",
        project=project,
        type_issue=issue_type,
        time_estimate_seconds=7200,
        jira_id=3001,
    )
    issue2 = Issue.objects.create(
        description="Another issue today",
        project=project,
        type_issue=issue_type,
        time_estimate_seconds=3600,
        jira_id=3002,
    )
    issue3 = Issue.objects.create(
        description="Issue without timeLog today",
        project=project,
        type_issue=issue_type,
        time_estimate_seconds=1800,
        jira_id=3003,
    )
    DimProjeto.objects.create(
        id_project_jiba=project.id,
        id_project_jira=project.jira_id,
        project_name=project.name,
        start_date=project.start_date_project,
    )

    DimTipoIssue.objects.create(
        id_type_jiba=issue_type.id,
        id_type_jira=issue_type.jira_id,
        name_type=issue_type.name,
    )

    # Criar TimeLogs - apenas issue1 e issue2 têm TimeLogs de hoje
    hoje = timezone.now()
    ontem = hoje - timedelta(days=1)

    TimeLog.objects.create(id_user=user, id_issue=issue1, seconds=3600, log_date=hoje, jira_id=501)
    TimeLog.objects.create(id_user=user, id_issue=issue2, seconds=1800, log_date=hoje, jira_id=502)
    a = TimeLog.objects.create(id_user=user, id_issue=issue3, seconds=900, log_date=ontem, jira_id=503)  # Ontem
    a.log_date = ontem
    a.save()

    service = DimIssueService()

    assert len(service.issues) == 2

    issue_data_1 = next((item for item in service.issues if item["issue"].id_issue_jira == 3001), None)
    issue_data_2 = next((item for item in service.issues if item["issue"].id_issue_jira == 3002), None)

    assert issue_data_1 is not None
    assert issue_data_2 is not None

    assert issue_data_1["total_minutos_hoje"] == 60.0  # 3600 segundos / 60
    assert issue_data_2["total_minutos_hoje"] == 30.0  # 1800 segundos / 60


@pytest.mark.django_db
def test_error_handling_missing_relations():
    """Testa tratamento de erros quando relações estão faltando"""
    # Setup com dados incompletos
    user = User.objects.create_user(
        username="error_user", email="error@test.com", password="pass123", valor_hora=60.0, jira_id=600
    )

    project = Project.objects.create(
        key="ERR",
        name="Error Project",
        description="Error test",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="err-uuid",
        jira_id=4001,
        projectTypeKey="software",
    )

    issue = Issue.objects.create(
        description="Error issue",
        project=project,
        time_estimate_seconds=3600,
        jira_id=5001,
        # Sem type_issue e status propositalmente
    )

    TimeLog.objects.create(id_user=user, id_issue=issue, seconds=1800, log_date=timezone.now(), jira_id=701)

    try:
        DimensionalService.generate_fact_worklog(TipoGranularidade.DIA)
        assert DimDev.objects.filter(id_dev_jira=600).exists()
        assert DimProjeto.objects.filter(id_project_jira=4001).exists()
    except Exception as e:
        assert isinstance(e, (IntegrityError, AttributeError, DimProjeto.DoesNotExist, DimTipoIssue.DoesNotExist))


@pytest.mark.django_db
def test_empty_data_scenarios():
    """Testa cenários com dados vazios"""
    intervalo_tempo_dia = DimIntervaloTemporalService(TipoGranularidade.DIA)
    service_dev = DimDevService()
    assert len(service_dev.devs) == 0

    service_issue = DimIssueService()
    assert len(service_issue.issues) == 0

    service_projeto = DimProjetoService(intervalo_tempo_dia)
    assert len(service_projeto.projetos_filtros) == 0

    service_types = DimIssueTypesService()
    assert len(service_types.issues_types) == 0

    service_status = DimStatusTypeService()
    assert len(service_status.status_types) == 0


@pytest.mark.django_db
def test_generate_project_snapshot_data_daily_mth(setup_issues_data):
    """Deve gerar snapshots diários e mensais corretamente"""

    ontem_timestamp = datetime.now() - timedelta(days=1)
    ontem = ontem_timestamp.strftime("%Y-%m-%d")
    with freeze_time(ontem):
        intervalo_tempo_dia = DimIntervaloTemporalService(TipoGranularidade.DIA)
        success = DimensionalService.generate_project_snapshot_data(intervalo_tempo_dia)

        assert success is True, "A geração de snapshot diário deve retornar True"

        snapshot_dia = FactProjectSnapshot.objects.all().first()
        assert snapshot_dia is not None, "Snapshot diário deve ser criado no FactProjectSnapshot"
        assert snapshot_dia.snapshot_interval.granularity_type == TipoGranularidade.DIA.value
        assert snapshot_dia.project.project_name == setup_issues_data.name
        assert snapshot_dia.total_accumulated_minutes == 0
        assert snapshot_dia.current_project_cost_rs == 0
        assert snapshot_dia.projection_end_days == 1
        assert snapshot_dia.minutes_left_end_project == 3060

    one_issue = Issue.objects.all()[0]
    one_issue.time_estimate_seconds = 28800
    one_issue.save()
    dev = User.objects.create_user(
        username="dev1",
        first_name="João",
        last_name="Silva",
        email="joao@example.com",
        password="pass123",
        valor_hora=75.0,
        jira_id=one_issue.id,
    )
    timelog = TimeLog.objects.create(
        id_issue=one_issue, id_user=dev, seconds=1800, log_date=timezone.now(), jira_id=one_issue.id
    )
    intervalo_tempo_dia = DimIntervaloTemporalService(TipoGranularidade.DIA)
    success_mes = DimensionalService.generate_project_snapshot_data(intervalo_tempo_dia)
    hoje = date.today()
    snapshot_dia = FactProjectSnapshot.objects.get(created_at__date=hoje)

    assert snapshot_dia is not None, "Snapshot diário deve ser criado no FactProjectSnapshot"
    assert snapshot_dia.snapshot_interval.granularity_type == TipoGranularidade.DIA.value
    assert snapshot_dia.project.project_name == setup_issues_data.name
    assert snapshot_dia.total_accumulated_minutes == 30
    assert snapshot_dia.current_project_cost_rs == (timelog.seconds / 3600) * dev.valor_hora
    assert snapshot_dia.projection_end_days == 2
    assert snapshot_dia.average_hour_value == 75

    assert success_mes is True, "A geração de snapshot mensal deve retornar True"
    intervalo_mes = DimIntervaloTemporalService(TipoGranularidade.MES)
    success_mes = DimensionalService.generate_project_snapshot_data(intervalo_mes)
    snapshot_mes = FactProjectSnapshot.objects.filter(
        snapshot_interval__granularity_type=TipoGranularidade.MES.value
    ).first()

    assert snapshot_mes is not None, "Snapshot mensal deve ser criado"
    assert snapshot_mes.snapshot_interval.start_date.month == timezone.now().month
    assert snapshot_mes.total_accumulated_minutes >= snapshot_dia.total_accumulated_minutes
    assert snapshot_mes.projection_end_days >= snapshot_dia.projection_end_days
    assert snapshot_mes.average_hour_value == 75
    assert snapshot_mes.total_accumulated_minutes == 30
