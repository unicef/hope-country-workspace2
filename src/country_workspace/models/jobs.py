from django.apps import apps
from django.db import models
from django.utils.module_loading import import_string

from django_celery_boost.models import CeleryTaskModel


class AsyncJob(CeleryTaskModel, models.Model):
    class JobType(models.TextChoices):
        FQN = "FQN", "Operation"
        ACTION = "ACTION", "Action"
        TASK = "TASK", "Task"

    type = models.CharField(max_length=50, choices=JobType.choices)
    program = models.ForeignKey("Program", related_name="jobs", on_delete=models.CASCADE)
    batch = models.ForeignKey("Batch", related_name="jobs", on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to="updates", null=True, blank=True)
    config = models.JSONField(default=dict, blank=True)
    action = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    celery_task_name = "country_workspace.tasks.sync_job_task"

    @property
    def queue_position(self) -> int:
        try:
            return super().queue_position
        except Exception:
            return 0

    @property
    def started(self) -> str:
        try:
            return self.task_info["started_at"]
        except Exception:
            return "="

    def execute(self):
        func = import_string(self.action)
        match self.type:
            case AsyncJob.JobType.FQN:
                return func(**self.config)
            case AsyncJob.JobType.ACTION:
                model = apps.get_model(self.config["model_name"])
                queryset = model.objects.filter(pk__in=self.config["pks"])
                return func(queryset, **self.config.get("kwargs", {}))
            case AsyncJob.JobType.TASK:
                return func(self)
