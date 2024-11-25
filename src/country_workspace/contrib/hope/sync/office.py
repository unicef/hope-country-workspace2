from typing import Optional

from hope_flex_fields.models import DataChecker

from country_workspace.models import Office, Program, SyncLog

from .. import constants
from ..client import HopeClient


def sync_offices() -> dict[str, int]:
    client = HopeClient()
    totals = {"add": 0, "upd": 0}
    for i, record in enumerate(client.get("business_areas")):
        if record["active"]:
            __, created = Office.objects.get_or_create(
                hope_id=record["id"],
                defaults={
                    "name": record["name"],
                    "slug": record["slug"],
                    "code": record["code"],
                    "active": record["active"],
                    "long_name": record["long_name"],
                },
            )
            if created:
                totals["add"] += 1
            else:
                totals["upd"] += 1
    SyncLog.objects.register_sync(Office)
    return totals


def sync_programs(limit_to_office: "Optional[Office]" = None) -> dict[str, int]:
    client = HopeClient()
    hh_chk = DataChecker.objects.filter(name=constants.HOUSEHOLD_CHECKER_NAME).first()
    ind_chk = DataChecker.objects.filter(name=constants.INDIVIDUAL_CHECKER_NAME).first()
    totals = {"add": 0, "upd": 0}
    if limit_to_office:
        office = limit_to_office
    for i, record in enumerate(client.get("programs")):
        try:
            if limit_to_office and record["business_area_code"] != office.code:
                continue
            else:
                office = Office.objects.get(code=record["business_area_code"])
            if record["status"] not in [Program.ACTIVE, Program.DRAFT]:
                continue
            p, created = Program.objects.get_or_create(
                hope_id=record["id"],
                defaults={
                    "name": record["name"],
                    "programme_code": record["programme_code"],
                    "status": record["status"],
                    "sector": record["sector"],
                    "country_office": office,
                },
            )
            if created:
                totals["add"] += 1
                p.household_checker = hh_chk
                p.individual_checker = ind_chk
                p.save()
            else:
                totals["upd"] += 1
        except Office.DoesNotExist:
            pass
    SyncLog.objects.register_sync(Program)
    return totals


def sync_all() -> bool:
    sync_offices()
    sync_programs()
    SyncLog.objects.refresh()
    return True
