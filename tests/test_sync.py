from django import forms

import pytest

from country_workspace.contrib.hope.sync.office import sync_all, sync_offices, sync_programs


@pytest.fixture(autouse=True)
def setup_definitions(db):
    from testutils.factories import FieldDefinitionFactory

    FieldDefinitionFactory(field_type=forms.ChoiceField)


@pytest.mark.vcr()
@pytest.mark.xdist_group("remote")
def test_sync_all():
    assert sync_all()


@pytest.mark.vcr()
@pytest.mark.xdist_group("remote")
def test_sync_programs():
    from country_workspace.models import Office

    assert sync_offices()
    assert sync_programs()

    office = Office.objects.first()

    assert sync_programs(office)
