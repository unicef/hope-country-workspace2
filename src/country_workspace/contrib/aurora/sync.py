from urllib.parse import urlparse
from django.core.cache import cache

from country_workspace.models import SyncLog
from country_workspace.contrib.aurora.models import Project, Registration
from country_workspace.contrib.aurora.client import AuroraClient


def sync_projects() -> dict[str, int]:
    """Synchronize projects from the Aurora system and updates the local database.

    Returns:
        dict[str, int]: A dictionary containing the number of projects added and updated:
            - "add": Number of new projects created.
            - "upd": Number of existing projects updated.

    """
    client = AuroraClient()
    totals = {"add": 0, "upd": 0}
    with cache.lock("sync-projects"):
        for record in client.get("project"):
            __, created = Project.objects.get_or_create(
                reference_pk=record["id"],
                defaults={
                    "name": record["name"],
                },
            )
            totals["add" if created else "upd"] += 1
        SyncLog.objects.register_sync(Project)
        return totals


def sync_registrations(limit_to_project: Project | None = None) -> dict[str, int]:
    """Synchronize registrations from the Aurora system and update the local database.

    Args:
        limit_to_project (Project | None, optional): If provided, only registrations
            related to this project will be synchronized.

    Returns:
        dict[str, int]: A dictionary with the number of registrations processed:
            - "add": Number of new registrations created.
            - "upd": Number of existing registrations updated.
            - "skip": Number of registrations skipped due to a missing project or an invalid project reference.

    """
    client = AuroraClient()
    totals = {"add": 0, "upd": 0, "skip": 0}
    with cache.lock("sync-registrations"):
        for record in client.get("registration"):
            extracted_id = _extract_project_id(record["project"])
            if extracted_id is None:
                totals["skip"] += 1
                continue

            try:
                project = limit_to_project if limit_to_project else Project.objects.get(reference_pk=extracted_id)
                __, created = project.registrations.get_or_create(
                    reference_pk=record["id"],
                    defaults={
                        "name": record["name"],
                        "active": record["active"],
                    },
                )
                totals["add" if created else "upd"] += 1
            except Project.DoesNotExist:
                totals["skip"] += 1

        SyncLog.objects.register_sync(Registration)
        return totals


def _extract_project_id(url: str) -> int | None:
    """Extract the project ID from the given URL.

    Args:
        url (str): The URL containing the project ID.

    Returns:
        int | None: The extracted project ID if successful, otherwise None.

    """
    parsed_url = urlparse(url)
    try:
        project_id_str = parsed_url.path.rstrip("/").split("/")[-1]
        return int(project_id_str)
    except (ValueError, IndexError):
        return None
