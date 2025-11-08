import datetime
import logging
from enum import Enum

from django.db.models import ExpressionWrapper, F, FloatField, Sum
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
    TimeLog,
)
from jiboia.core.service import issue_status_svc, issues_type_svc, projects_svc

logger = logging.getLogger(__name__)


class TipoGranularidade(Enum):
    DIA = "Dia"
    SEMANA = "Semana"
    MES = "Mês"
    TRIMESTRE = "Trimestre"
    SEMESTRE = "Semestre"
    ANO = "Ano"


class DimensionalService:
    @classmethod
    def generate_project_snapshot_data(cls, time_interval):
        logger.info(
            "[DIM LOAD]: Iniciando geração de snapshot de projetos para intervalo: %s", time_interval.dimtemporal
        )
        projects_filter = DimProjetoService(time_interval)
        result = cls.save_fact_project_snapshot(projects_filter, time_interval)
        logger.info("[DIM LOAD]: Geração de snapshot de projetos concluída.")
        return result

    @classmethod
    def generate_fact_issue(cls, time_interval):
        logger.info("[DIM LOAD]: Iniciando geração de Fato Issues para intervalo: %s", time_interval.dimtemporal)
        projetos = DimProjetoService(time_interval)
        issue_types = DimIssueTypesService()
        status_types = DimStatusTypeService()
        result = cls.save_fact_issue(projetos, issue_types, status_types, time_interval)
        logger.info("[DIM LOAD]: Geração de Fato Issues concluída.")
        return result

    @classmethod
    def generate_fact_worklog(cls, time_interval):
        logger.info("[DIM LOAD]: Iniciando geração de Fato Worklogs para intervalo: %s", time_interval.dimtemporal)
        devs = DimDevService()
        projects_filter = DimProjetoService(time_interval)
        result = cls.save_fact_worklog(time_interval, projects_filter, devs)
        logger.info("[DIM LOAD]: Geração de Fato Worklogs concluída.")
        return result

    @classmethod
    def save_fact_project_snapshot(cls, project_filter, dimtemporal):
        logger.info(
            "[DIM LOAD]: Salvando FactProjectSnapshot. Total de projetos a processar: %s",
            len(project_filter.projetos_filtros),
        )
        for proj in project_filter.projetos_filtros:
            proj_instance = FactProjectSnapshot.objects.create(
                project=proj["project"],
                snapshot_interval=dimtemporal.dimtemporal,
                current_project_cost_rs=proj["current_project_cost_rs"],
                total_accumulated_minutes=proj["total_accumulated_minutes"],
                projection_end_days=proj["projection_end_days"],
            )
            logger.debug(
                "[DIM LOAD]: FactProjectSnapshot criado. ID: %s, Projeto: %s, Intervalo: %s",
                proj_instance.id,
                proj_instance.project,
                proj_instance.snapshot_interval,
            )
        logger.info("[DIM LOAD]: FactProjectSnapshot salvo com sucesso para o intervalo: %s", dimtemporal.dimtemporal)
        return True

    @classmethod
    def save_fact_issue(cls, projetos, issue_types, status_types, intervalo_tempo):
        logger.info(
            "[DIM LOAD]: Salvando FactIssue. Projetos: %s, Tipos de Issue: %s, Status: %s",
            len(projetos.projetos_filtros),
            len(issue_types.issues_types),
            len(status_types.status_types),
        )
        for projeto in projetos.projetos_filtros:
            logger.debug("[DIM LOAD]: Processando projeto para FactIssue: %s", projeto["project"])
            for issue_type in issue_types.issues_types:
                for status in status_types.status_types:
                    total_issue = Issue.objects.filter(
                        project__jira_id=projeto["id_project_jira"],
                        type_issue__jira_id=issue_type["id_type_jira"],
                        status__jira_id=status["id_status_jira"],
                    ).count()
                    # garantir que sem status sejam no_status

                    FactIssue.objects.create(
                        project=projeto["project"],
                        issue_type=issue_type["issue_type"],
                        status=status["dimstatus"],
                        total_issue=total_issue if total_issue else 0,
                        worklog_interval=intervalo_tempo.dimtemporal,
                    )
                    logger.debug(
                        "[DIM LOAD]: FactIssue criado. Projeto: %s, Tipo: %s, Status: %s, Total: %s",
                        projeto["project"],
                        issue_type["issue_type"],
                        status["dimstatus"],
                        total_issue,
                    )
        logger.info("[DIM LOAD]: FactIssue salvo com sucesso para o intervalo: %s", intervalo_tempo.dimtemporal)
        return True

    @classmethod
    def save_fact_worklog(cls, worklog_interval, projects_filter, all_devs):
        logger.info(
            "[DIM LOAD]: Salvando FactEsforco. Intervalo: %s, Projetos: %s, Desenvolvedores: %s",
            worklog_interval.dimtemporal,
            len(projects_filter.projetos_filtros),
            len(all_devs.devs),
        )
        grouped_effort = projects_filter.worklog_interval
        logger.debug("[DIM LOAD]: Worklogs agrupados obtidos. Total de itens agrupados: %s", len(grouped_effort))
        mapa = {(item["id_user"], item["id_issue__project_id"]): item["total_seconds"] for item in grouped_effort}

        for dev in all_devs.devs:
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
                logger.debug(
                    "[DIM LOAD]: FactEsforco criado. Dev: %s, Projeto: %s, Minutos: %s, Custo: %.2f",
                    dev["dev"],
                    projeto["project"],
                    total_minutes,
                    accumulated_cost,
                )
        logger.info("[DIM LOAD]: FactEsforco salvo com sucesso para o intervalo: %s", worklog_interval.dimtemporal)
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
        dim_dev, _ = DimDev.objects.update_or_create(
            id_dev_jiba=dev["id"],
            defaults={
                "id_dev_jira": dev["jira_id"],
                "dev_name": dev["username"],
                "valor_hora": dev["valor_hora"],
            },
        )
        return dim_dev


class DimProjetoService:
    def __init__(self, intervalo_temporal_service):
        self.start_date = intervalo_temporal_service.start_date
        self.end_date = intervalo_temporal_service.end_date
        self.projetos_filtros = self.filters_projects()
        self.worklog_interval = self.worklog_group()

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
                "current_project_cost_rs": self.current_project_cost_rs(
                    projeto_id=projeto_id,
                    start_date=self.start_date,
                    end_date=self.end_date,
                ),
                "total_accumulated_minutes": self.total_accumulated_minutes(
                    projeto_id=projeto_id,
                    start_date=self.start_date,
                    end_date=self.end_date,
                ),
                "projection_end_days": self.projection_end_days(projeto_id=projeto_id),
            }
            filtros.append(filtro)
        return filtros

    def current_project_cost_rs(self, projeto_id=None, start_date=None, end_date=None):
        """
        Calcula o custo real do projeto baseado nos TimeLogs (worklogs) registrados
        dentro do intervalo pesquisado.
        """
        result = (
            TimeLog.objects.filter(
                id_issue__project_id=projeto_id,
                log_date__gte=start_date,
                log_date__lt=end_date,
            )
            .annotate(
                custo=ExpressionWrapper((F("seconds") / 3600.0) * F("id_user__valor_hora"), output_field=FloatField())
            )
            .aggregate(project_cost_rs=Sum("custo"))
        )
        return result.get("project_cost_rs") or 0.0

    def total_accumulated_minutes(self, projeto_id=None, start_date=None, end_date=None):
        total_minutes = TimeLog.objects.filter(
            id_issue__project_id=projeto_id,
            log_date__gte=start_date,
            log_date__lt=end_date,
        ).aggregate(minutos=Sum(F("seconds") / 60.0, output_field=FloatField()))
        return total_minutes.get("minutos") or 0

    def projection_end_days(self, projeto_id: int):
        total_seconds_agg = Issue.objects.filter(project_id=projeto_id).aggregate(
            total_seconds=Sum("time_estimate_seconds", output_field=FloatField())
        )
        total_time_in_sec = total_seconds_agg.get("total_seconds") or 0.0

        if total_time_in_sec <= 0:
            return 0.0
        UTIL_SECONDS_PER_DAY = 28800  # 8 horas
        return total_time_in_sec / UTIL_SECONDS_PER_DAY

    def save_or_create_dim_projeto(self, project):
        try:
            dim_project, _ = DimProjeto.objects.update_or_create(
                id_project_jiba=project["project_id"],
                defaults={
                    "id_project_jira": project["jira_id"],
                    "start_date": project["start_date_project"],
                    "project_name": project["name"],
                    "end_date": project["end_date_project"],
                },
            )
        except Exception as e:
            logger.error(
                "[DIM LOAD]: Erro ao criar/atualizar DimProjeto para projeto ID %s: %s", project["project_id"], str(e)
            )
            raise e
        return dim_project

    def worklog_group(self):
        esforcos_agrupados = (
            TimeLog.objects.filter(log_date__gte=self.start_date, log_date__lt=self.end_date)
            .values("id_user", "id_issue__project_id")
            .annotate(total_seconds=Sum("seconds"))
        )
        return esforcos_agrupados


class DimIntervaloTemporalService:
    def __init__(self, granularity_type: TipoGranularidade, refer: datetime.datetime = None):
        self.granularity_type = granularity_type
        self.start_date, self.end_date = type(self).create_interval(granularity_type, refer)
        self.dimtemporal = self.save_dimtemporal()

    @classmethod
    def create_interval(cls, tipo: TipoGranularidade, refer: datetime.datetime = None):
        if refer is None:
            refer = timezone.now()

        interval_methods = {
            TipoGranularidade.DIA: cls._interval_dia,
            TipoGranularidade.SEMANA: cls._interval_semana,
            TipoGranularidade.MES: cls._interval_mes,
            TipoGranularidade.TRIMESTRE: cls._interval_trimestre,
            TipoGranularidade.SEMESTRE: cls._interval_semestre,
            TipoGranularidade.ANO: cls._interval_ano,
        }
        try:
            return interval_methods[tipo](refer)
        except KeyError:
            raise ValueError("Tipo de granularidade inválido")

    @staticmethod
    def _interval_dia(refer):
        start_date = refer.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + datetime.timedelta(days=1)
        return start_date, end_date

    @staticmethod
    def _interval_semana(refer):
        start_date = refer - datetime.timedelta(days=refer.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + datetime.timedelta(weeks=1)
        return start_date, end_date

    @staticmethod
    def _interval_mes(refer):
        start_date = refer.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if refer.month == 12:
            end_date = start_date.replace(year=refer.year + 1, month=1)
        else:
            end_date = start_date.replace(month=refer.month + 1)
        return start_date, end_date

    @staticmethod
    def _interval_trimestre(refer):
        mes_base = ((refer.month - 1) // 3) * 3 + 1
        start_date = refer.replace(month=mes_base, day=1, hour=0, minute=0, second=0, microsecond=0)
        if mes_base == 10:
            end_date = start_date.replace(year=refer.year + 1, month=1)
        else:
            end_date = start_date.replace(month=mes_base + 3)
        return start_date, end_date

    @staticmethod
    def _interval_semestre(refer):
        mes_base = 1 if refer.month <= 6 else 7
        start_date = refer.replace(month=mes_base, day=1, hour=0, minute=0, second=0, microsecond=0)
        if mes_base == 7:
            end_date = start_date.replace(year=refer.year + 1, month=1)
        else:
            end_date = start_date.replace(month=7)
        return start_date, end_date

    @staticmethod
    def _interval_ano(refer):
        start_date = refer.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date.replace(year=refer.year + 1)
        return start_date, end_date

    def save_dimtemporal(self):
        self.dimtemporal = DimIntervaloTemporal.objects.create(
            granularity_type=self.granularity_type.value,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        return self.dimtemporal

    @classmethod
    def create_interval_retro(
        cls,
        tipo: TipoGranularidade,
        issues_breakdown_months: int = 0,
        refer: datetime.datetime = None,
    ):
        """
        Cria múltiplos intervalos retroativos com base na granularidade e quantidade de meses.
        Exemplo: gerar intervalos para os últimos 3 meses.
        """
        if refer is None:
            refer = timezone.now()

        interval_methods = {
            TipoGranularidade.DIA: cls._interval_dia,
            TipoGranularidade.SEMANA: cls._interval_semana,
            TipoGranularidade.MES: lambda r: cls._interval_mes_retro(r, issues_breakdown_months),
            TipoGranularidade.TRIMESTRE: cls._interval_trimestre,
            TipoGranularidade.SEMESTRE: cls._interval_semestre,
            TipoGranularidade.ANO: cls._interval_ano,
        }

        try:
            return interval_methods[tipo](refer)
        except KeyError:
            raise ValueError("Tipo de granularidade inválido")

    @staticmethod
    def _interval_mes_retro(refer, months_back: int):
        """
        Retorna um dicionário com os intervalos dos últimos N meses a partir da data de referência.
        Usa a mesma lógica de _interval_mes.
        """
        interval_dict = {}
        for i in range(months_back):
            month = refer.month - i
            year = refer.year
            if month <= 0:
                month += 12
                year -= 1

            ref_date = refer.replace(year=year, month=month)

            start_date, end_date = DimIntervaloTemporalService._interval_mes(ref_date)
            key = f"{ref_date.year}-{ref_date.month:02d}"
            interval_dict[key] = {
                "start_date": start_date,
                "end_date": end_date,
            }

        return interval_dict


class DimIssueTypesService:
    def __init__(self):
        self.issues_types = self._create_types_issues()

    def _create_types_issues(self):
        issues_type = issues_type_svc.list_type_issues()
        filtros = []

        for issue_type in issues_type:
            dim_issuetype = self._get_or_create_issue_type(issue_type)
            self.create_or_update_dim_issue(issue_type, dim_issuetype)

            filtro = {
                "issue_type": dim_issuetype,
                "id_type_jira": dim_issuetype.id_type_jira,
                "id_type_jiba": dim_issuetype.id_type_jiba,
                "name_type": dim_issuetype.name_type,
            }
            filtros.append(filtro)

        return filtros

    def _get_or_create_issue_type(self, issue_type):
        dim_issue_type, _ = DimTipoIssue.objects.update_or_create(
            id_type_jiba=issue_type["issuetype_id"],
            id_type_jira=issue_type["jira_id"],
            defaults={
                "name_type": issue_type["name"],
            },
        )
        return dim_issue_type

    def create_or_update_dim_issue(self, issue_type, dim_issuetype):
        issues_from_type = Issue.objects.filter(type_issue__jira_id=issue_type["jira_id"]).select_related(
            "project", "type_issue"
        )
        for issue in issues_from_type:
            DimIssue.objects.update_or_create(
                id_issue_jiba=issue.id,
                id_issue_jira=issue.jira_id,
                defaults={
                    "project": DimProjeto.objects.get(id_project_jiba=issue.project.id),
                    "issue_type": dim_issuetype,
                    "start_date": issue.start_date,
                },
            )


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
                "key": dim_status_type.key,
            }
            filtros.append(filtro)

        return filtros

    def _get_or_create_status_type(self, status):
        """Busca ou cria um registro de DimStatus."""
        dim_status, _ = DimStatus.objects.update_or_create(
            id_status_jira=status["jira_id"],
            id_status_jiba=status["statustype_id"],
            defaults={"status_name": status["name"], "key": status["key"]},
        )
        return dim_status


class DimIssueService:
    def __init__(self):
        self.issues = self._create_issues()

    def _create_issues(self):
        now = timezone.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + datetime.timedelta(days=1)

        issues_with_sum = (
            TimeLog.objects.filter(log_date__gte=start, log_date__lt=end)
            .select_related("id_issue", "id_issue__project", "id_issue__type_issue", "id_user")
            .annotate(total_seconds=Sum("seconds"))
        )
        filtros = []
        for issue in issues_with_sum:
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

    def _get_or_create_issue(self, timelog):
        issue = timelog.id_issue
        dim_issue, _ = DimIssue.objects.update_or_create(
            id_issue_jiba=issue.id,
            id_issue_jira=issue.jira_id,
            defaults={
                "project": DimProjeto.objects.get(id_project_jiba=issue.project.id),
                "issue_type": DimTipoIssue.objects.get(id_type_jiba=issue.type_issue.id),
                "start_date": issue.start_date,
            },
        )
        return dim_issue
