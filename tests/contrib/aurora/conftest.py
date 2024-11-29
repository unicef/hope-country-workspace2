from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import vcr
from extras.testutils.factories import (
    AsyncJobFactory,
    BatchFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from pytest_mock import MockerFixture

from country_workspace.contrib.aurora.client import AuroraClient
from country_workspace.models import AsyncJob


@pytest.fixture
def mock_vcr() -> vcr.VCR:
    return vcr.VCR(
        filter_headers=["authorization"],
        cassette_library_dir=str(Path(__file__).parent.parent.parent / "extras/cassettes"),
        record_mode=vcr.record_mode.RecordMode.ONCE,
        match_on=("path",),
    )


@pytest.fixture
def mock_aurora_data() -> dict[str, Any]:
    return {
        "cassette_name": "sync_aurora_4pages.yaml",
        "pages": 4,
        "records_per_page": 10,
        "households": 1,
        "individuals": 2,
        "results": [
            {
                "fields": {
                    "household": [{"field_hh1": "value_hh1"}],
                    "individuals": [
                        {"field_i1": "value_i1"},
                        {"field_i2": "value_i2"},
                    ],
                }
            }
        ],
        "form_cleaned_data": {
            "batch_name": "Batch 1",
            "household_name_column": "family_name",
        },
        # "imported_by_id": 1,
    }


@pytest.fixture
def mock_aurora_client(mocker: MockerFixture, mock_aurora_data: dict[str, Any]) -> MagicMock:
    client = mocker.MagicMock(spec=AuroraClient)
    client.get.return_value = mock_aurora_data["results"]
    return client


@pytest.fixture
def program():
    return ProgramFactory()


@pytest.fixture
def batch(program):
    return BatchFactory(program=program)


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def job(mock_aurora_data, program, batch, user):
    return AsyncJobFactory(
        type=AsyncJob.JobType.TASK,
        program=program,
        batch=batch,
        owner=user,
        config={
            **mock_aurora_data["form_cleaned_data"],
            "imported_by_id": user.pk,
        },
    )


@pytest.fixture
def household(batch):
    return HouseholdFactory(batch=batch)


@pytest.fixture
def individuals(batch, household):
    return IndividualFactory.create_batch(2, batch=batch, household=household)
