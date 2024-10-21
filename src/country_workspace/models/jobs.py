from django.apps import apps
from django.db import models
from django.utils.module_loading import import_string

import sentry_sdk
from django_celery_boost.models import CeleryTaskModel


class AsyncJob(CeleryTaskModel, models.Model):
    class JobType(models.TextChoices):
        FQN = "FQN", "Operation"
        ACTION = "ACTION", "Action"
        TASK = "TASK", "Task"
        BULK_UPDATE_HH = "BULK_UPDATE_HH"
        BULK_UPDATE_IND = "BULK_UPDATE_IND"
        AURORA_SYNC = "AURORA_SYNC"

    type = models.CharField(max_length=50, choices=JobType.choices)
    program = models.ForeignKey("Program", related_name="jobs", on_delete=models.CASCADE)
    batch = models.ForeignKey("Batch", related_name="jobs", on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to="updates", null=True, blank=True)
    config = models.JSONField(default=dict, blank=True)
    action = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    sentry_id = models.CharField(max_length=255, blank=True, null=True)
    celery_task_name = "country_workspace.tasks.sync_job_task"

    def __str__(self):
        return self.description or f"Background Job #{self.pk}"

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
        sid = None
        try:
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
        except Exception as e:
            sid = sentry_sdk.capture_exception(e)
            raise e
        finally:
            if sid:
                self.sentry_id = sid
                self.save(update_fields=["sentry_id"])
