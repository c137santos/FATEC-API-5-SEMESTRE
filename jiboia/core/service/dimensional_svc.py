import datetime
from datetime import timedelta
from enum import Enum

from django.db.models import F, FloatField, Sum
from django.utils import timezone

from jiboia.accounts import services
from jiboia.core.models import (
    DimDev,
    DimIntervaloTemporal,
    DimIssue,
    DimProjeto,
    DimStatus,
    DimTipoIssue,
    FactEsforco,
    FactIssue,
    FactProjectSnapshot,
    Issue,
    Project,
    TimeLog,
)
from jiboia.core.service import issue_status_svc, issues_type_svc, projects_svc


class TipoGranularidade(Enum):
    DIA = "Dia"
    SEMANA = "Semana"
    MES = "Mês"
    TRIMESTRE = "Trimestre"
    SEMESTRE = "Semestre"
    ANO = "Ano"


class DimensionalService:
    @classmethod
    def generate_project_snapshot_data(cls, granularity_type: TipoGranularidade):
        intervalo_tempo = DimIntervaloTemporalService(granularity_type)
        projects_filter = DimProjetoService()
        return cls.save_fact_project_snapshot(projects_filter, intervalo_tempo)

    @classmethod
    def generate_fact_issue(cls, granularity_type):
        intervalo_tempo = DimIntervaloTemporalService(granularity_type)
        projetos = DimProjetoService()
        issue_types = DimIssueTypesService()
        status_types = DimStatusTypeService()
        return cls.save_fact_issue(projetos, issue_types, status_types, intervalo_tempo)

    @classmethod
    def generate_fact_worklog(cls, granularity_type):
        devs = DimDevService()
        projects_filter = DimProjetoService()
        worklog_interval = DimIntervaloTemporalService(granularity_type)
        return cls.save_fact_worklog(worklog_interval, projects_filter, devs)

    @classmethod
    def save_fact_project_snapshot(cls, project_filter, dimtemporal):
        for proj in project_filter.projetos_filtros:
            proj_instace = FactProjectSnapshot.objects.create(
                project=proj["project"],
                snapshot_interval=dimtemporal.dimtemporal,
                current_project_cost_rs=proj["current_project_cost_rs"],
                total_accumulated_minutes=proj["total_accumulated_minutes"],
                projection_end_days=proj["projection_end_days"],
            )
            print(proj_instace)
        return True

    @classmethod
    def save_fact_issue(cls, projetos, issue_types, status_types, intervalo_tempo):
        for projeto in projetos.projetos_filtros:
            for issue_type in issue_types.issues_types:
                for status in status_types.status_types:
                    total_issue = Issue.objects.filter(
                        project__jira_id=projeto["id_project_jira"],
                        type_issue__jira_id=issue_type["id_type_jira"],
                        status__jira_id=status["id_status_jira"],
                    ).count()

                    FactIssue.objects.create(
                        project=projeto["project"],
                        issue_type=issue_type["issue_type"],
                        status=status["dimstatus"],
                        total_issue=total_issue if total_issue else 0,
                        worklog_interval=intervalo_tempo.dimtemporal,
                    )
        return True

    @classmethod
    def save_fact_worklog(cls, worklog_interval, projects_filter, todos_devs):
        esforcos_agrupados = projects_filter.worklog_group()
        mapa = {(item["id_user"], item["id_issue__project_id"]): item["total_seconds"] for item in esforcos_agrupados}
        for dev in todos_devs.devs:
            for projeto in projects_filter.projetos_filtros:
                total_seconds = mapa.get((dev["id_dev_jiba"], projeto["id_project_jiba"]), 0)
                total_minutes = total_seconds // 60
                valor_hora = dev["valor_hora"] or 0
                accumulated_cost = (total_minutes / 60) * float(valor_hora)
                FactEsforco.objects.create(
                    dev=dev["dev"],
                    project=projeto["project"],
                    worklog_interval=worklog_interval.dimtemporal,
                    accumulated_minutes=total_minutes,
                    accumulated_cost=accumulated_cost,
                )
        return True


class DimDevService:
    def __init__(self):
        self.devs = self._create_devs()

    def _create_devs(self):
        devs = services.list_users()
        filtros = []

        for dev in devs:
            dim_dev = self._get_or_create_dev(dev)

            filtro = {
                "dev": dim_dev,
                "id_dev_jiba": dim_dev.id_dev_jiba,
                "id_dev_jira": dim_dev.id_dev_jira,
                "dev_name": dim_dev.dev_name,
                "valor_hora": dim_dev.valor_hora,
            }
            filtros.append(filtro)

        return filtros

    def _get_or_create_dev(self, dev):
        dim_dev = DimDev.objects.filter(id_dev_jiba=dev["id"]).first()
        if not dim_dev:
            dim_dev = DimDev.objects.create(
                id_dev_jiba=dev["id"],
                id_dev_jira=dev["jira_id"],
                dev_name=dev["username"],
                valor_hora=dev["valor_hora"],
            )
        return dim_dev


class DimProjetoService:
    def __init__(self):
        self.projetos_filtros = self.filters_projects()

    def filters_projects(self):
        projects = projects_svc.list_all_projects()
        filtros = []

        for project in projects:
            dim_project = self.save_or_create_dim_projeto(project)

            projeto_id = project["project_id"]
            filtro = {
                "project": dim_project,
                "id_project_jiba": projeto_id,
                "id_project_jira": project["jira_id"],
                "project_name": project["name"],
                "start_date": project["start_date_project"],
                "end_date": project["end_date_project"],
                "current_project_cost_rs": self.current_project_cost_rs(projeto_id=projeto_id),
                "total_accumulated_minutes": self.total_accumulated_minutes(projeto_id=projeto_id),
                "projection_end_days": self.projection_end_days(projeto_id=projeto_id),
            }
            filtros.append(filtro)
        return filtros

    @classmethod
    def current_project_cost_rs(cls, projeto_id=None):
        result = (
            Project.objects.filter(id=projeto_id)
            .annotate(
                project_cost_rs=Sum(
                    (F("issue__time_estimate_seconds") / 3600.0) * F("issue__id_user__valor_hora"),
                    output_field=FloatField(),
                )
            )
            .values("project_cost_rs")
            .first()
        )

        return result.get("project_cost_rs") or 0.0

    @classmethod
    def total_accumulated_minutes(cls, projeto_id=None):
        total_minutos = TimeLog.objects.filter(id_issue__project_id=projeto_id).aggregate(
            minutos=Sum(F("seconds") / 60.0, output_field=FloatField())
        )
        return total_minutos.get("minutos") or 0

    @classmethod
    def projection_end_days(cls, projeto_id: int):
        total_seconds_agg = Issue.objects.filter(project_id=projeto_id).aggregate(
            total_seconds=Sum("time_estimate_seconds", output_field=FloatField())
        )
        tempo_total_em_segundos = total_seconds_agg.get("total_seconds") or 0.0

        if tempo_total_em_segundos <= 0:
            return 0.0
        else:
            SEGUNDOS_POR_DIA_UTIL = 28800
            dias_uteis_necessarios = tempo_total_em_segundos / SEGUNDOS_POR_DIA_UTIL
            return dias_uteis_necessarios

    @classmethod
    def save_or_create_dim_projeto(cls, project):
        dim_project = DimProjeto.objects.filter(id_project_jiba=project["project_id"]).first()
        if not dim_project:
            dim_project = DimProjeto.objects.create(
                id_project_jiba=project["project_id"],
                id_project_jira=project["jira_id"],
                start_date=project["start_date_project"],
                project_name=project["name"],
            )
        return dim_project

    @classmethod
    def worklog_group(cls):
        agora = timezone.now()
        start = agora.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        esforcos_agrupados = (
            TimeLog.objects.filter(log_date__gte=start, log_date__lt=end)
            .values("id_user", "id_issue__project_id")
            .annotate(total_seconds=Sum("seconds"))
        )
        return esforcos_agrupados


class DimIntervaloTemporalService:
    def __init__(self, granularity_type: TipoGranularidade):
        self.granularity_type = granularity_type
        self.start_date, self.end_date = self.create_interval(granularity_type)
        self.dimtemporal = self.save_dimtemporal()

    def create_interval(self, tipo: TipoGranularidade, refer: datetime.datetime = None):  # noqa C901
        if refer is None:
            refer = datetime.datetime.now()

        if tipo == TipoGranularidade.DIA:
            start_date = refer.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + datetime.timedelta(days=1)

        elif tipo == TipoGranularidade.SEMANA:
            # início na segunda-feira
            start_date = refer - datetime.timedelta(days=refer.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + datetime.timedelta(weeks=1)

        elif tipo == TipoGranularidade.MES:
            start_date = refer.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if refer.month == 12:
                end_date = start_date.replace(year=refer.year + 1, month=1)
            else:
                end_date = start_date.replace(month=refer.month + 1)

        elif tipo == TipoGranularidade.TRIMESTRE:
            mes_base = ((refer.month - 1) // 3) * 3 + 1
            start_date = refer.replace(month=mes_base, day=1, hour=0, minute=0, second=0, microsecond=0)
            if mes_base == 10:
                end_date = start_date.replace(year=refer.year + 1, month=1)
            else:
                end_date = start_date.replace(month=mes_base + 3)

        elif tipo == TipoGranularidade.SEMESTRE:
            mes_base = 1 if refer.month <= 6 else 7
            start_date = refer.replace(month=mes_base, day=1, hour=0, minute=0, second=0, microsecond=0)
            if mes_base == 7:
                end_date = start_date.replace(year=refer.year + 1, month=1)
            else:
                end_date = start_date.replace(month=7)

        elif tipo == TipoGranularidade.ANO:
            start_date = refer.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(year=refer.year + 1)

        else:
            raise ValueError("Tipo de granularidade inválido")

        return start_date, end_date

    def save_dimtemporal(self):
        self.dimtemporal = DimIntervaloTemporal.objects.create(
            granularity_type=self.granularity_type.value,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        return self.dimtemporal


class DimIssueTypesService:
    def __init__(self):
        self.issues_types = self._create_types_issues()

    def _create_types_issues(self):
        issues_type = issues_type_svc.list_type_issues()
        filtros = []

        for issue in issues_type:
            dim_issuetype = self._get_or_create_issue_type(issue)

            filtro = {
                "issue_type": dim_issuetype,
                "id_type_jira": dim_issuetype.id_type_jira,
                "id_type_jiba": dim_issuetype.id_type_jiba,
                "name_type": dim_issuetype.name_type,
            }
            filtros.append(filtro)

        return filtros

    def _get_or_create_issue_type(self, issue_type):
        dim_issue_type = DimTipoIssue.objects.filter(id_type_jiba=issue_type["issuetype_id"]).first()
        if not dim_issue_type:
            dim_issue_type = DimTipoIssue.objects.create(
                id_type_jira=issue_type["jira_id"],
                id_type_jiba=issue_type["issuetype_id"],
                name_type=issue_type["name"],
            )
        return dim_issue_type


class DimStatusTypeService:
    def __init__(self):
        self.status_types = self._create_status_types()

    def _create_status_types(self):
        status_type_list = issue_status_svc.list_status_type()
        filtros = []

        for status in status_type_list:
            dim_status_type = self._get_or_create_status_type(status)

            filtro = {
                "dimstatus": dim_status_type,
                "id": dim_status_type.id,
                "id_status_jiba": dim_status_type.id_status_jiba,
                "id_status_jira": dim_status_type.id_status_jira,
                "status_name": dim_status_type.status_name,
            }
            filtros.append(filtro)

        return filtros

    def _get_or_create_status_type(self, status):
        """Busca ou cria um registro de DimTipoIssue."""
        dim_issue_type = DimStatus.objects.filter(id_status_jira=status["jira_id"]).first()

        if not dim_issue_type:
            dim_issue_type = DimStatus.objects.create(
                id_status_jira=status["jira_id"],
                id_status_jiba=status["statustype_id"],
                status_name=status["name"],
            )

        return dim_issue_type

    @classmethod
    def get_all_dim_status(cls):
        filtros = []
        varias_dims = DimStatus.objects.all()
        for dim_status_type in varias_dims:
            filtro = {
                "dimstatus": dim_status_type,
                "id": dim_status_type.id,
                "id_status_jiba": dim_status_type.id_status_jiba,
                "id_status_jira": dim_status_type.id_status_jira,
                "status_name": dim_status_type.status_name,
            }
            filtros.append(filtro)
        return filtros


class DimIssueService:
    def __init__(self):
        self.issues = self._create_issues()

    def _create_issues(self):
        agora = timezone.now()
        start = agora.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        issues_com_soma = (
            TimeLog.objects.filter(log_date__gte=start, log_date__lt=end)
            .select_related("id_issue", "id_issue__project", "id_issue__type_issue", "id_user")
            .annotate(total_seconds=Sum("seconds"))
        )
        filtros = []
        for issue in issues_com_soma:
            total_seconds = issue.total_seconds or 0
            total_minutos_hoje = total_seconds / 60.0

            dim_issue = self._get_or_create_issue(issue)

            filtros.append(
                {
                    "dev": issue.id_user,
                    "valor_hora": issue.id_user.valor_hora,
                    "issue": dim_issue,
                    "status": issue.id_issue.status,
                    "id_issue_jiba": dim_issue.id_issue_jiba,
                    "id_issue_jira": dim_issue.id_issue_jira,
                    "projeto_id": issue.id_issue.project.id,
                    "start_date": issue.id_issue.start_date,
                    "end_date": issue.id_issue.end_date,
                    "time_estimate_seconds": issue.id_issue.time_estimate_seconds,
                    "total_minutos_hoje": total_minutos_hoje,
                }
            )

        return filtros

    def _get_or_create_issue(self, issue):
        dim_issue = DimIssue.objects.filter(id=issue.id).first()
        if not dim_issue:
            dim_issue = DimIssue.objects.create(
                id_issue_jiba=issue.id,
                id_issue_jira=issue.jira_id,
                projeto=DimProjeto.objects.get(id_project_jiba=issue.id_issue.project.id),
                issue_type=DimTipoIssue.objects.get(id_type_jiba=issue.id_issue.type_issue.id),
                start_date=issue.id_issue.start_date,
            )
        return dim_issue
