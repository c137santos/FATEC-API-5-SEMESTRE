from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone


class Issue(models.Model):
    description = models.CharField(max_length=512, help_text="Título ou descrição curta")
    details = models.TextField(blank=True, help_text="Descrição longa ou detalhes adicionais")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data e hora de criação")
    start_date = models.DateTimeField(blank=True, null=True, help_text="Data de início planejada ou real")
    end_date = models.DateTimeField(blank=True, null=True, help_text="Data de término planejada ou real")
    time_estimate_seconds = models.IntegerField(
        blank=True, null=True, help_text="Estimativa de tempo para conclusão, em segundos"
    )

    id_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_user",
        help_text="O usuário responsável",
    )

    project = models.ForeignKey(
        "Project", null=True, on_delete=models.CASCADE, help_text="O projeto ao qual a issue pertence"
    )
    type_issue = models.ForeignKey(
        "IssueType", on_delete=models.SET_NULL, null=True, help_text="O tipo da issue (ex: História, Tarefa, Bug)"
    )
    status = models.ForeignKey(
        "StatusType", on_delete=models.SET_NULL, null=True, blank=True, help_text="O status atual da issue"
    )
    jira_id = models.IntegerField(null=True, help_text="Identificador único da issue no Jira")

    class Meta:
        db_table = "issue"
        verbose_name = "Issue"
        verbose_name_plural = "Issues"

    def __str__(self):
        return f"Issue #{self.id} - {self.description[:50]}"

    def to_dict_json(self):
        return {
            "id": self.id,
            "description": self.description,
            "status": {"id": self.status.id, "name": self.status.name} if self.status else None,
            "created_at": self.created_at.isoformat(),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
        }


# }/rest/api/3/issuetype
class IssueType(models.Model):
    name = models.CharField(max_length=255, help_text="Nome do tipo de issue (ex: História, Tarefa, Bug)")
    description = models.TextField(help_text="Descrição detalhada do tipo")
    subtask = models.BooleanField(default=False, help_text="Indica se este tipo é uma subtarefa")
    jira_id = models.IntegerField(unique=True, help_text="Identificador único do tipo de issue no Jira")

    class Meta:
        db_table = "type_issue"
        verbose_name = "Issue Type"
        verbose_name_plural = "Issue Types"

    def __str__(self):
        return self.name


class Project(models.Model):
    key = models.CharField(max_length=50, unique=True, help_text="A sigla identificadora")
    name = models.CharField(max_length=255, help_text="Nome do projeto")
    description = models.TextField(help_text="Descrição detalhada do projeto")
    start_date_project = models.DateField(null=True, blank=True, help_text="Data de início do projeto")
    end_date_project = models.DateField(null=True, blank=True, help_text="Data limite de conclusão")
    uuid = models.TextField(unique=True, help_text="Identificador único do Jira")
    jira_id = models.IntegerField(unique=True, help_text="Identificador numérico do Jira")
    projectTypeKey = models.CharField(max_length=100, help_text="Tipo do projeto no Jira")

    class Meta:
        db_table = "projeto"
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.name


class TimeLog(models.Model):
    id_issue = models.ForeignKey(
        Issue, on_delete=models.CASCADE, help_text="Referência para a Issue à qual este log de tempo pertence"
    )
    id_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuário que registrou o tempo",
    )
    seconds = models.IntegerField(help_text="Quantidade de tempo registrada, em segundos")
    log_date = models.DateTimeField(auto_now_add=True, help_text="Data e hora em que o tempo foi registrado")
    description_log = models.TextField(help_text="Descrição ou comentário sobre o trabalho realizado")
    jira_id = models.IntegerField(unique=True, help_text="Identificador único do log de tempo no Jira")

    class Meta:
        db_table = "log_tempo"
        verbose_name = "Time Log"
        verbose_name_plural = "Time Logs"

    def __str__(self):
        return f"Time log for issue #{self.id_issue_id}"


# }/rest/api/3/status
class StatusType(models.Model):
    key = models.CharField(max_length=255, help_text="Chave para categoria")
    name = models.TextField(help_text="Nome do status")
    jira_id = models.IntegerField(unique=True, help_text="Identificador único do Jira")

    class Meta:
        db_table = "type_status"
        verbose_name = "Status Type"
        verbose_name_plural = "Status Types"

    def __str__(self):
        return self.name


class DimProjeto(models.Model):
    id = models.AutoField(primary_key=True)
    id_projeto_jiba = models.IntegerField(unique=True, db_index=True, help_text="ID Projeto no jiboia")
    id_projeto_jira = models.IntegerField(unique=True, db_index=True, help_text="ID Projeto no jira")
    nome_projeto = models.CharField(max_length=255)
    data_inicio = models.DateField()
    data_fim = models.DateField()

    class Meta:
        db_table = "dim_projeto"
        verbose_name = "Dimensão Projeto"

    def __str__(self):
        return self.nome_projeto


class DimDev(models.Model):
    id = models.AutoField(primary_key=True, help_text="ID Natural do Desenvolvedor")
    nome_dev = models.CharField(max_length=255)
    id_dev_jiba = models.IntegerField(db_index=True, help_text="ID do Desenvolvedor no jiboia")
    id_dev_jira = models.IntegerField(db_index=True, help_text="ID do Desenvolvedor no jira")
    valor_hora = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "dim_dev"
        verbose_name = "Dimensão Desenvolvedor"

    def __str__(self):
        return f"Dev {self.id}"


class DimStatus(models.Model):
    id = models.AutoField(primary_key=True, help_text="ID Natural do Status")
    id_status_jira = models.IntegerField(db_index=True, help_text="ID do Status no jira")
    id_status_jiba = models.IntegerField(db_index=True, help_text="ID do Status no jiboia")
    nome_status = models.CharField(max_length=100)

    class Meta:
        db_table = "dim_status"
        verbose_name = "Dimensão Status"

    def __str__(self):
        return self.nome_status


class DimTipoIssue(models.Model):
    id = models.AutoField(primary_key=True, help_text="ID Natural do Tipo de Issue")
    id_tipo_jira = models.IntegerField(help_text="ID do Tipo de Issue no jira")
    id_tipo_jiba = models.IntegerField(help_text="ID do Tipo de Issue no jiboia")
    nome_tipo = models.CharField(max_length=100)

    class Meta:
        db_table = "dim_tipo_issue"
        verbose_name = "Dimensão Tipo de Issue"

    def __str__(self):
        return self.nome_tipo


class DimIntervaloTemporal(models.Model):
    class TipoGranularidade(models.TextChoices):
        DIA = "DIA", "Dia"
        SEMANA = "SEMANA", "Semana"
        MES = "MES", "Mês"
        TRIMESTRE = "TRIMESTRE", "Trimestre"
        SEMESTRE = "SEMESTRE", "Semestre"
        ANO = "ANO", "Ano"

    id = models.AutoField(primary_key=True, help_text="ID Natural do Intervalo Temporal")
    tipo_granularidade = models.CharField(
        max_length=50, choices=TipoGranularidade.choices, help_text="Tipo de Período (Dia, Mês, etc.)"
    )
    data_inicio = models.DateTimeField(null=True, blank=True, help_text="Data de inicio em dias, horas e segundos")
    data_fim = models.DateTimeField(null=True, blank=True, help_text="Data de fim em dias, horas e segundos")

    class Meta:
        db_table = "dim_intervalo_temporal"
        verbose_name = "Dimensão Intervalo Temporal"

    @property
    def duracao_total_minutos(self):
        """Retorna a duração total em minutos"""
        if self.data_fim and self.data_inicio:
            delta = self.data_fim - self.data_inicio
            return int(delta.total_seconds() / 60)
        return 0


class FatoProjetoSnapshot(models.Model):
    projeto = models.ForeignKey(DimProjeto, on_delete=models.PROTECT, verbose_name="Projeto")
    intervalo_snapshot = models.ForeignKey(
        DimIntervaloTemporal,
        on_delete=models.PROTECT,
        related_name="snapshots_projeto",
        help_text="Período do Snapshot",
    )
    versao_carga = models.DateTimeField(help_text="Data de criação do snapshot")
    projecao_termino_dias = models.IntegerField(
        help_text="Somatória dos dias previsto em todas as issues não finalizadas"
    )
    custo_do_projeto_atual_rs = models.DecimalField(
        max_digits=15, decimal_places=2, help_text="Somatória das horas dos devs trabalhadas * valor hora respectivo"
    )
    total_horas_acumuladas = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Total de horas já gastas em desenvolvimento"
    )
    total_issues = models.IntegerField(help_text="Total de issues no projeto")

    class Meta:
        db_table = "fato_projeto_snapshot"
        verbose_name = "Fato Projeto Snapshot"
        unique_together = (("projeto", "intervalo_snapshot"),)

    @property
    def valor_hora_media(self):
        """
        help: Valor médio da hora trabalhada (gastos_acumulados_reais / total_horas_acumuladas)
        """
        if self.total_horas_acumuladas > 0:
            return self.custo_do_projeto_atual_rs / self.total_horas_acumuladas
        return 0

    @property
    def minutos_faltando_fim_projeto(self):
        """
        help: Quantidade de minutos faltando para o fim do projeto (baseado na data atual e data_fim do projeto)
        """
        if not self.projeto.data_fim:
            return None

        agora = timezone.now()
        data_fim_projeto = timezone.make_aware(datetime.combine(self.projeto.data_fim, datetime.min.time()))

        delta = data_fim_projeto - agora
        return max(int(delta.total_seconds() / 60), 0)

    @property
    def tempo_medio_conclusao_issues(self):
        """
        help: Tempo médio de conclusão da issue
        """
        if self.total_issues > 0:
            return self.total_horas_acumuladas / self.total_issues
        return 0


class FatoIssue(models.Model):
    id = models.AutoField(primary_key=True)
    projeto = models.ForeignKey(
        DimProjeto, on_delete=models.PROTECT, verbose_name="Projeto", help_text="Projeto ao qual a Issue pertence"
    )
    dev = models.ForeignKey(
        DimDev, on_delete=models.PROTECT, verbose_name="Desenvolvedor", help_text="Desenvolvedor que trabalhou na Issue"
    )
    status = models.ForeignKey(
        DimStatus, on_delete=models.PROTECT, verbose_name="Status da Issue", help_text="Status atual da Issue"
    )
    tipo_issue = models.ForeignKey(
        DimTipoIssue,
        on_delete=models.PROTECT,
        verbose_name="Tipo da Issue",
        help_text="Tipo da Issue (História, Tarefa, Bug, etc.)",
    )

    data_criacao = models.DateTimeField(help_text="Data de Criação da Issue")
    intervalo_trabalho = models.ForeignKey(
        DimIntervaloTemporal,
        on_delete=models.PROTECT,
        related_name="esforco_issue",
        help_text="Período do Esforço empregado na Issue",
    )
    id_issue_jiba = models.IntegerField(db_index=True, help_text="ID Original da Issue no jiboia")
    id_issue_jira = models.CharField(db_index=True, help_text="ID Original da Issue no jira")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data de criação no modelo dimensional")

    class Meta:
        db_table = "fato_issue"
        verbose_name = "Fato Issue"
        indexes = [
            models.Index(fields=["projeto", "dev", "data_criacao", "intervalo_trabalho"]),
        ]

    @property
    def minutos_gastos(self):
        """
        Calcula as horas gastas baseado no intervalo_trabalho
        """
        if self.intervalo_trabalho:
            return self.intervalo_trabalho.duracao_total_minutos
        return 0
