from django.db import models
from django.utils import timezone

from concurrency.api import concurrency_disable_increment
from django_celery_boost.models import CeleryTaskModel


class AsyncJob(CeleryTaskModel, models.Model):

    class JobType(models.TextChoices):
        FQN = "FQN", "Task"
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
    repeatable = models.BooleanField(default=False, blank=True, help_text="Indicate if the job can be repeated as-is")

    owner = models.ForeignKey("User", related_name="jobs", on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Creation date and time")
    request_timestamp = models.DateTimeField("Queued At", blank=True, null=True, help_text="Queueing date and time")

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

    def queue(self, use_version: bool = True) -> str | None:
        if self.task_status not in self.ACTIVE_STATUSES:
            res = self.task_handler.delay(self.pk, self.version if use_version else None)
            with concurrency_disable_increment(self):
                self.request_timestamp = timezone.now()
                self.curr_async_result_id = res.id
                self.save(update_fields=["curr_async_result_id", "request_timestamp"])
            return self.curr_async_result_id
        return None

    def is_terminated(self) -> bool:
        """Check if the job is queued"""
        return self.curr_async_result_id and self.task_status not in self.ACTIVE_STATUSES
