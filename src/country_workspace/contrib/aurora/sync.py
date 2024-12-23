from typing import Any

from django.db.transaction import atomic

from country_workspace.contrib.aurora.client import AuroraClient
from country_workspace.models import AsyncJob, Batch, Household, Individual
from country_workspace.utils.fields import clean_field_name


def sync_aurora_job(job: AsyncJob) -> dict[str, int]:
    """Synchronize data from the Aurora system into the database for the given job within an atomic transaction.

    Args:
        job (AsyncJob): The job instance containing configuration and context for synchronization.

    Returns:
        dict[str, int]: A dictionary with counts of households and individuals created.

    """
    batch_name = job.config["batch_name"]
    batch = Batch.objects.create(
        name=batch_name,
        program=job.program,
        country_office=job.program.country_office,
        imported_by=job.owner,
        source=Batch.BatchSource.RDI,
    )
    total_hh = total_ind = 0
    client = AuroraClient()
    with atomic():
        for record in client.get("record"):
            for f_name, f_value in record["fields"].items():
                if f_name == "household":
                    hh = _create_household(batch, f_value[0])
                    total_hh += 1
                elif f_name == "individuals":
                    total_ind += len(_create_individuals(hh, f_value, job.config.get("household_name_column", None)))

    return {"households": total_hh, "individuals": total_ind}


def _create_household(batch: Batch, fields: dict[str, Any]) -> Household:
    """Create a household entity associated with the given job and batch.

    Args:
        batch (Batch): The job instance containing context for household creation.
        fields (dict[str, Any]): A dictionary containing household data fields.

    Returns:
        Household: The newly created household instance.

    """
    return batch.program.households.create(batch=batch, flex_fields={clean_field_name(k): v for k, v in fields.items()})


def _create_individuals(
    household: Household, data: list[dict[str, Any]], household_name_column: str
) -> list[Individual]:
    """Create individuals associated with a household and updates the household name if necessary.

    Args:
        household (Household): The household to associate with the individuals.
        data (list[dict[str, Any]]): A list of dictionaries containing individual data fields.
        household_name_column (str): The name of the column in household that contains the name of the individuals.

    Returns:
        list[Individual]: The list of newly created individual instances.

    """
    individuals = []
    head_found = False
    for individual in data:
        if not head_found:
            head_found = _update_household_name_from_individual(household, individual, household_name_column)

        fullname = next((k for k in individual if k.startswith("given_name")), None)
        individuals.append(
            Individual(
                batch=household.batch,
                household_id=household.pk,
                name=individual.get(fullname, ""),
                flex_fields={clean_field_name(k): v for k, v in individual.items()},
            )
        )

    return household.program.individuals.bulk_create(individuals)


def _update_household_name_from_individual(
    household: Household, individual: dict[str, Any], household_name_column: str
) -> bool:
    """Update the household name based on an individual's relationship and name field.

    This method checks if the individual is marked as the head of the household
    and updates the household name accordingly.

    Args:
        household (Household): The household to update.
        individual (dict[str, Any]): The individual data containing potential household name information.
        household_name_column (str): The name of the column in household that contains the name of the individuals.

    Returns:
        None

    """
    if any(individual.get(k) == "head" for k in individual if k.startswith("relationship")):
        for k, v in individual.items():
            if clean_field_name(k) == household_name_column:
                household.name = v
                household.save()
                return True
