from django.db import models
from django.conf import settings


class Issue(models.Model):
    description = models.CharField(max_length=512, help_text="Título ou descrição curta da issue")
    done = models.BooleanField(default=False, help_text="Indica se a issue foi concluída")
    details = models.TextField(blank=True, help_text="Descrição longa ou detalhes adicionais da issue")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data e hora de criação da issue")
    start_date = models.DateTimeField(blank=True, null=True, help_text="Data de início planejada ou real da issue")
    end_date = models.DateTimeField(blank=True, null=True, help_text="Data de término planejada ou real da issue")
    time_estimate_seconds = models.IntegerField(blank=True, null=True, help_text="Estimativa de tempo para completar a issue, em segundos")
    
    id_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_user', help_text="O usuário responsável pela issue")
    
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        help_text="O projeto ao qual a issue pertence"
    )
    jira_id = models.IntegerField(unique=True, help_text="Identificador único da issue no Jira")

    class Meta:
        db_table = 'issue'
        verbose_name = 'Issue'
        verbose_name_plural = 'Issues'

    def __str__(self):
        # ATENÇÃO: O correto é self.id, pois o Django cria o campo 'id' automaticamente
        return f"Issue #{self.id} - {self.description[:50]}"

    def to_dict_json(self):
        return {
            "id": self.id,
            "description": self.description,
            "done": self.done,
        }

#}/rest/api/3/issuetype
class IssueType(models.Model):
    name = models.CharField(max_length=255, help_text="Nome do tipo de issue (ex: História, Tarefa, Bug)")
    description = models.TextField(help_text="Descrição detalhada do tipo de issue")
    subtask = models.BooleanField(default=False, help_text="Indica se este tipo de issue é uma subtarefa")
    jira_id = models.IntegerField(unique=True, help_text="Identificador único do tipo de issue no Jira")

    class Meta:
        db_table = 'type_issue'
        verbose_name = 'Issue Type'
        verbose_name_plural = 'Issue Types'

    def __str__(self):
        return self.name

class Project(models.Model):
    key = models.CharField(max_length=50, unique=True, help_text="A sigla identificadora")
    name = models.CharField(max_length=255, help_text="Nome do projeto")
    description = models.TextField(help_text="Descrição do projeto")
    start_date_project = models.DateField(help_text="Data de início do projeto")
    end_date_project = models.DateField(null=True, blank=True, help_text="Data limite de conclusão")
    uuid = models.IntegerField(unique=True, help_text="Identificador único do Jira")
    jira_id = models.IntegerField(unique=True, help_text="Identificador numérico do Jira")


    class Meta:
        db_table = 'projeto'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.name_project

class TimeLog(models.Model):
    id_issue = models.ForeignKey(Issue, on_delete=models.CASCADE, db_column='id_issue', help_text="Referência para a Issue à qual este log de tempo pertence")
    id_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_user', help_text="Usuário que registrou o tempo")
    seconds = models.IntegerField(help_text="Quantidade de tempo registrada, em segundos")
    log_date = models.DateTimeField(auto_now_add=True, help_text="Data e hora em que o tempo foi registrado")
    description_log = models.TextField(help_text="Descrição ou comentário sobre o trabalho realizado")
    jira_id = models.IntegerField(unique=True, help_text="Identificador único do log de tempo no Jira")
    
    class Meta:
        db_table = 'log_tempo'
        verbose_name = 'Time Log'
        verbose_name_plural = 'Time Logs'

    def __str__(self):
        return f"Time log for issue #{self.id_issue_id}"

#}/rest/api/3/status
class StatusType(models.Model):
    key = models.CharField(max_length=255, help_text="Chave para categoria") 
    name = models.TextField(help_text="Nome do status")
    jira_id = models.IntegerField(unique=True, help_text="Identificador único do Jira")

    class Meta:
        db_table = 'type_status'
        verbose_name = 'Status Type'
        verbose_name_plural = 'Status Types'

    def __str__(self):
        return self.name
class StatusLog(models.Model):
    id_issue = models.ForeignKey(Issue, on_delete=models.CASCADE, db_column="id_issue", help_text="Id conexão tabela Issue")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data de criação do log")
    old_status = models.CharField(
        StatusType,
        db_column='old_status',
        help_text="Id conexão com Status que represente o anterior"
    )
    new_status = models.CharField(
        StatusType,
        db_column='new_status',
        help_text="Id conexão com Status que represente o atual"
    )
    class Meta:
        db_table = 'status_log'
        verbose_name = 'Status Log'
        verbose_name_plural = 'Status Logs'

    def __str__(self):
        return f"Status of issue #{self.id_issue_id} changed from {self.old_status} to {self.new_status}"
    