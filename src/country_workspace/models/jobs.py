from django.db import models

from django_celery_boost.models import CeleryTaskModel


class AsyncJob(CeleryTaskModel, models.Model):
    class JobType(models.TextChoices):
        BULK_UPDATE_HH = "BULK_UPDATE_HH"
        BULK_UPDATE_IND = "BULK_UPDATE_IND"
        CREATE_XLS_IMPORTER = "CREATE_XLS_IMPORTER"
        VALIDATE_PROGRAM = "VALIDATE_PROGRAM"

    type = models.CharField(max_length=50, choices=JobType.choices)
    program = models.ForeignKey("Program", related_name="jobs", on_delete=models.CASCADE)
    batch = models.ForeignKey("Batch", related_name="jobs", on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to="updates", null=True, blank=True)
    config = models.JSONField(default=dict, blank=True)
    action = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    owner = models.ForeignKey("User", related_name="jobs", on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

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
