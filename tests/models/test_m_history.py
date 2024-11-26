import pytest

from country_workspace.models import Household
from country_workspace.workspaces.models import CountryHousehold


@pytest.fixture()
def household() -> "CountryHousehold":
    from testutils.factories.household import CountryHouseholdFactory, get_hh_fields

    ff = get_hh_fields(None)
    ff["size"] = 99
    return CountryHouseholdFactory(flex_fields=ff, flex_files=b"1111")


def test_last_changes(household: "Household"):
    old = household.checksum
    household.flex_fields["size"] = 2
    household.save()
    household.refresh_from_db()
    assert household.checksum != old
    assert household.flex_fields["size"] == 2
    assert household.last_changes() == [("change", "size", (99, 2))]


def test_diff(household: "Household"):
    household.flex_fields["size"] = 11
    household.save()
    household.flex_fields["size"] = 12
    household.save()
    household.flex_fields["size"] = 13
    household.save()
    household.refresh_from_db()
    assert household.diff() == [("change", "size", (13, 12))]
    assert household.diff(-1) == [("change", "size", (13, 12))]
    assert household.diff(-1, -2) == [("change", "size", (13, 12))]
    assert household.diff(-2, -3) == [("change", "size", (12, 11))]
    assert household.diff(-3, -4) == [("change", "size", (11, 99))]
