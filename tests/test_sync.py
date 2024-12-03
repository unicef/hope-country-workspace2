from pathlib import Path

from django import forms

import pytest
from responses import _recorder

from country_workspace.contrib.hope.sync.office import sync_all, sync_offices, sync_programs


@pytest.fixture(autouse=True)
def setup_definitions(db):
    from testutils.factories import FieldDefinitionFactory

    FieldDefinitionFactory(field_type=forms.ChoiceField)


def test_sync_all():
    assert _recorder.record(file_path=Path(__file__).parent / "r_sync_programs1.yaml")(sync_all)()


def test_sync_programs():
    from country_workspace.models import Office

    @_recorder.record(file_path=Path(__file__).parent / "r_sync_programs1.yaml")
    def doit():
        assert sync_offices()
        assert sync_programs()

    doit()
    office = Office.objects.first()

    @_recorder.record(file_path=Path(__file__).parent / "r_sync_program2.yaml")
    def doit():
        assert sync_programs(office)

    doit()
