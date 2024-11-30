import json
from pathlib import Path
from unittest.mock import patch

import pytest
from constance.test.unittest import override_config

from country_workspace.contrib.aurora.sync import (
    _create_household,
    _create_individuals,
    _update_household_name_from_individual,
    sync_aurora_job,
)
from country_workspace.models import Household


def test_create_household_success(mock_aurora_data, batch):
    fields = mock_aurora_data["results"][0]["fields"]["household"][0]
    household = _create_household(batch, fields)

    assert isinstance(household, Household)
    assert household.program == batch.program
    assert household.batch == batch
    assert household.country_office == batch.program.country_office
    assert household.flex_fields == fields


@pytest.mark.parametrize(
    "data, expected_name_update",
    [
        (
            {"relationship_to_head": "head", "family_name": "Head Of Household Name"},
            "Head Of Household Name",
        ),
        (
            {"relationship_to_head": "child", "family_name": "Child Name"},
            None,
        ),
        (
            {"relationship_to_head": "head"},
            None,
        ),
        (
            {},
            None,
        ),
    ],
    ids=[
        "Head with name update",
        "Non-head individual",
        "Head without name",
        "Empty individual data",
    ],
)
def test_update_household_name_from_individual(mock_aurora_data, household, data, expected_name_update):
    initial_name = household.name

    individual_data = mock_aurora_data["results"][0]["fields"]["individuals"][0].copy()
    individual_data.update(data)
    _update_household_name_from_individual(household, individual_data, household_name_column="family_name")
    household.refresh_from_db()

    if expected_name_update:
        assert household.name == expected_name_update
    else:
        assert household.name == initial_name


@pytest.mark.parametrize(
    "data, expected_count",
    [
        (
            [
                {"given_name": "John", "family_name": "Doe", "relationship_to_head": "head"},
                {"given_name": "Jane", "family_name": "Doe", "relationship_to_head": "spouse"},
            ],
            2,
        ),
        (
            [],
            0,
        ),
    ],
    ids=["filled_fields", "empty_fields"],
)
def test_create_individuals(mock_aurora_data, household, data, expected_count):
    with (
        patch(
            "country_workspace.contrib.aurora.sync.clean_field_name", side_effect=lambda x: f"cleaned_{x}"
        ) as mock_clean_field_name,
    ):

        individuals = _create_individuals(household, data, household_name_column="family_name")

        assert len(individuals) == expected_count

        if expected_count > 0:
            for individual, data in zip(individuals, data):
                assert individual.household_id == household.pk
                assert individual.batch == household.batch
                assert individual.name == data.get("given_name", "")
                assert individual.flex_fields == {f"cleaned_{k}": v for k, v in data.items()}
                mock_clean_field_name.assert_any_call("given_name")


@override_config(AURORA_API_URL="https://api.aurora.io")
def test_sync_aurora_job_success_new(mocked_responses, job):
    mocked_responses.add(
        mocked_responses.GET,
        "https://api.aurora.io/record/",
        json=json.loads((Path(__file__).parent / "aurora.json").read_text()),
        status=200,
    )

    result = sync_aurora_job(job)
    assert result == {"households": 2, "individuals": 3}


# def test_sync_aurora_job_success(mock_aurora_client, mock_aurora_data, job, household, individuals):
#     with (
#         patch("country_workspace.contrib.aurora.sync.AuroraClient", return_value=mock_aurora_client),
#         patch("country_workspace.contrib.aurora.sync._create_batch", return_value=job.batch) as mock_create_batch,
#         patch(
#             "country_workspace.contrib.aurora.sync._create_household", return_value=household
#         ) as mock_create_household,
#         patch(
#             "country_workspace.contrib.aurora.sync._create_individuals", return_value=individuals
#         ) as mock_create_individuals,
#         patch.object(job, "save", wraps=job.save) as mock_save_job,
#     ):
#         mock_aurora_client.get.return_value = mock_aurora_data["results"]
#
#         result = sync_aurora_job(job)
#
#         mock_create_batch.assert_called_once_with(job)
#         assert mock_aurora_client.get.called
#         mock_create_household.assert_called_once_with(job, mock_aurora_data["results"][0]["fields"]["household"][0])
#         mock_create_individuals.assert_called_once_with(
#             job, household, mock_aurora_data["results"][0]["fields"]["individuals"]
#         )
#
#         assert mock_save_job.call_count == 1
#
#         assert result == {
#             "households": 1,
#             "individuals": len(individuals),
#         }
