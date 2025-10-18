import datetime
from enum import Enum

from django.db.models import F, FloatField, Sum

from jiboia.core.models import (
    DimIntervaloTemporal,
    DimProjeto,
    DimStatus,
    DimTipoIssue,
    FatoIssue,
    FatoProjetoSnapshot,
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


class DimenssionalService:
    @classmethod
    def load_fact_issue(cls, tipo_granularidade) -> dict:
        intervalo_tempo = DimIntervaloTemporalService(tipo_granularidade)
        projetos = DimProjetoService()
        issue_types = DimIssueTypesService()
        status_types = DimStatusTypeService()

        for projeto in projetos.projetos_filtros:
            for issue_type in issue_types.issues_types:
                for status in status_types.status_types:
                    total_issue = Issue.objects.filter(
                        project__jira_id=projeto["id_projeto_jira"],
                        type_issue__jira_id=issue_type["id_tipo_jira"],
                        status__jira_id=status["id_status_jira"],
                    ).count()

                    FatoIssue.objects.create(
                        projeto=projeto["project"],
                        tipo_issue=issue_type["issue_type"],
                        status=status["dimstatus"],
                        total_issue=total_issue if total_issue else 0,
                        intervalo_trabalho=intervalo_tempo.dimtemporal,
                    )

    @classmethod
    def load_fato_projeto_snapshot(cls, tipo_granularidade: TipoGranularidade) -> dict:
        intervalo_tempo = DimIntervaloTemporalService(tipo_granularidade)
        intervalo_tempo.save_dimtemporal()
        projects_filter = DimProjetoService()
        cls.save_fact_issue_snapshot(projects_filter, intervalo_tempo)
        return True

    @classmethod
    def save_fact_issue_snapshot(cls, project_filter, dimtemporal):
        for proj in project_filter.projetos_filtros:
            proj_instace = FatoProjetoSnapshot.objects.create(
                projeto=proj["project"],
                intervalo_snapshot=dimtemporal.dimtemporal,
                custo_projeto_atual_rs=proj["custo_projeto_atual_rs"],
                total_minutos_acumulados=proj["total_minutos_acumulados"],
                projecao_termino_dias=proj["projecao_termino_dias"],
            )
            print(proj_instace)


class DimProjetoService:
    def __init__(self):
        self.projetos_filtros = self.projetos_filtrados()

    def projetos_filtrados(self):
        projects = projects_svc.list_all_projects()
        filtros = []

        for project in projects:
            dim_project = self.save_or_create_dim_projeto(project)

            projeto_id = project["project_id"]
            filtro = {
                "project": dim_project,
                "id_projeto_jiba": projeto_id,
                "id_projeto_jira": project["jira_id"],
                "nome_projeto": project["name"],
                "data_inicio": project["start_date_project"],
                "data_fim": project["end_date_project"],
                "custo_projeto_atual_rs": self.custo_projeto_atual_rs(projeto_id=projeto_id),
                "total_minutos_acumulados": self.total_minutos_acumulados(projeto_id=projeto_id),
                "projecao_termino_dias": self.projecao_termino_dias(projeto_id=projeto_id),
            }
            filtros.append(filtro)
        return filtros

    @classmethod
    def custo_projeto_atual_rs(cls, projeto_id=None):
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
    def total_minutos_acumulados(cls, projeto_id=None):
        total_minutos = TimeLog.objects.filter(id_issue__project_id=projeto_id).aggregate(
            minutos=Sum(F("seconds") / 60.0, output_field=FloatField())
        )
        return total_minutos.get("minutos") or 0

    @classmethod
    def projecao_termino_dias(cls, projeto_id: int):
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
        dim_project = DimProjeto.objects.filter(id_projeto_jiba=project["project_id"]).first()
        if not dim_project:
            dim_project = DimProjeto.objects.create(
                id_projeto_jiba=project["project_id"],
                id_projeto_jira=project["jira_id"],
                data_inicio=project["start_date_project"],
                nome_projeto=project["name"],
            )
        return dim_project


class DimIntervaloTemporalService:
    def __init__(self, tipo_granularidade: TipoGranularidade):
        self.tipo_granularidade = tipo_granularidade
        self.data_inicio, self.data_fim = self.criar_intervalo(tipo_granularidade)
        self.dimtemporal = self.save_dimtemporal()

    def criar_intervalo(self, tipo: TipoGranularidade, referencia: datetime.datetime = None):  # noqa C901
        if referencia is None:
            referencia = datetime.datetime.now()

        if tipo == TipoGranularidade.DIA:
            data_inicio = referencia.replace(hour=0, minute=0, second=0, microsecond=0)
            data_fim = data_inicio + datetime.timedelta(days=1)

        elif tipo == TipoGranularidade.SEMANA:
            # início na segunda-feira
            data_inicio = referencia - datetime.timedelta(days=referencia.weekday())
            data_inicio = data_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
            data_fim = data_inicio + datetime.timedelta(weeks=1)

        elif tipo == TipoGranularidade.MES:
            data_inicio = referencia.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if referencia.month == 12:
                data_fim = data_inicio.replace(year=referencia.year + 1, month=1)
            else:
                data_fim = data_inicio.replace(month=referencia.month + 1)

        elif tipo == TipoGranularidade.TRIMESTRE:
            mes_base = ((referencia.month - 1) // 3) * 3 + 1
            data_inicio = referencia.replace(month=mes_base, day=1, hour=0, minute=0, second=0, microsecond=0)
            if mes_base == 10:
                data_fim = data_inicio.replace(year=referencia.year + 1, month=1)
            else:
                data_fim = data_inicio.replace(month=mes_base + 3)

        elif tipo == TipoGranularidade.SEMESTRE:
            mes_base = 1 if referencia.month <= 6 else 7
            data_inicio = referencia.replace(month=mes_base, day=1, hour=0, minute=0, second=0, microsecond=0)
            if mes_base == 7:
                data_fim = data_inicio.replace(year=referencia.year + 1, month=1)
            else:
                data_fim = data_inicio.replace(month=7)

        elif tipo == TipoGranularidade.ANO:
            data_inicio = referencia.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            data_fim = data_inicio.replace(year=referencia.year + 1)

        else:
            raise ValueError("Tipo de granularidade inválido")

        return data_inicio, data_fim

    def save_dimtemporal(self):
        self.dimtemporal = DimIntervaloTemporal.objects.create(
            tipo_granularidade=self.tipo_granularidade.value,
            data_inicio=self.data_inicio,
            data_fim=self.data_fim,
        )
        return self.dimtemporal


class DimIssueTypesService:
    def __init__(self):
        self.issues_types = self._create_types_issues()

    def _create_types_issues(self):
        issues_type = issues_type_svc.list_issues()
        filtros = []

        for issue in issues_type:
            dim_issuetype = self._get_or_create_issue_type(issue)

            filtro = {
                "issue_type": dim_issuetype,
                "id_tipo_jira": issue["jira_id"],
                "id_tipo_jiba": issue["issuetype_id"],
                "nome_tipo": issue["name"],
            }
            filtros.append(filtro)

        return filtros

    def _get_or_create_issue_type(self, issue_type):
        dim_issue_type = DimTipoIssue.objects.filter(id_tipo_jiba=issue_type["issuetype_id"]).first()
        if not dim_issue_type:
            dim_issue_type = DimTipoIssue.objects.create(
                id_tipo_jira=issue_type["jira_id"],
                id_tipo_jiba=issue_type["issuetype_id"],
                nome_tipo=issue_type["name"],
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
                "nome_status": dim_status_type.nome_status,
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
                nome_status=status["name"],
            )

        return dim_issue_type
