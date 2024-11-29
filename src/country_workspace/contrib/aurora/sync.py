from typing import Any

from django.db.transaction import atomic

from country_workspace.contrib.aurora.client import AuroraClient
from country_workspace.models import AsyncJob, Batch, Household, Individual
from country_workspace.utils.fields import clean_field_name


def sync_aurora_job(job: AsyncJob) -> dict[str, int]:
    """
    Synchronizes data from the Aurora system into the database for the given job within an atomic transaction.

    Args:
        job (AsyncJob): The job instance containing configuration and context for synchronization.

    Returns:
        dict[str, int]: A dictionary with counts of households and individuals created.
    """
    total_hh = total_ind = 0
    client = AuroraClient()
    with atomic():
        for record in client.get("record"):
            for f_name, f_value in record["fields"].items():
                if f_name == "household":
                    hh = _create_household(job, f_value[0])
                    total_hh += 1
                elif f_name == "individuals":
                    total_ind += len(_create_individuals(job, hh, f_value))

    return {"households": total_hh, "individuals": total_ind}


def _create_batch(job: AsyncJob) -> Batch:
    """
    Creates a batch entity associated with the given job.

    Args:
        job (AsyncJob): The job instance containing the configuration for the batch creation.

    Returns:
        Batch: The newly created batch instance.
    """
    return Batch.objects.create(
        name=job.config.get("batch_name"),
        program=job.program,
        country_office=job.program.country_office,
        imported_by=job.owner,
    )


def _create_household(job: AsyncJob, fields: dict[str, Any]) -> Household:
    """
    Creates a household entity associated with the given job and batch.

    Args:
        job (AsyncJob): The job instance containing context for household creation.
        fields (dict[str, Any]): A dictionary containing household data fields.

    Returns:
        Household: The newly created household instance.
    """
    return job.program.households.create(
        batch=job.batch, flex_fields={clean_field_name(k): v for k, v in fields.items()}
    )


def _create_individuals(
    job: AsyncJob,
    household: Household,
    fields: list[dict[str, Any]],
) -> list[Individual]:
    """
    Creates individuals associated with a household and updates the household name if necessary.

    Args:
        job (AsyncJob): The job instance containing configuration and context for individual creation.
        household (Household): The household to associate with the individuals.
        fields (list[dict[str, Any]]): A list of dictionaries containing individual data fields.

    Returns:
        list[Individual]: The list of newly created individual instances.
    """
    individuals = []
    for individual in fields:

        _update_household_name_from_individual(job, household, individual)

        fullname = next((k for k in individual if k.startswith("given_name")), None)
        individuals.append(
            Individual(
                batch=job.batch,
                household_id=household.pk,
                name=individual.get(fullname, ""),
                flex_fields={clean_field_name(k): v for k, v in individual.items()},
            )
        )

    return job.program.individuals.bulk_create(individuals)


def _update_household_name_from_individual(job: AsyncJob, household: Household, individual: dict[str, Any]) -> None:
    """
    Updates the household name based on an individual's relationship and name field.

    This method checks if the individual is marked as the head of the household
    and updates the household name accordingly.

    Args:
        job (AsyncJob): The job instance containing configuration details.
        household (Household): The household to update.
        individual (dict[str, Any]): The individual data containing potential household name information.

    Returns:
        None
    """
    if any(individual.get(k) == "head" for k in individual if k.startswith("relationship")):
        for k, v in individual.items():
            if clean_field_name(k) == job.config["household_name_column"]:
                job.program.households.filter(pk=household.pk).update(name=v)
                break
