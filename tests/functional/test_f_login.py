import pytest

pytestmark = pytest.mark.xdist_group("selenium")


@pytest.fixture
def office(db, worker_id):
    from testutils.factories import OfficeFactory

    return OfficeFactory()


@pytest.fixture
def program(office, worker_id):
    from testutils.factories import CountryProgramFactory

    return CountryProgramFactory(
        country_office=office,
        household_columns="__str__\nid\nxx",
        individual_columns="__str__\nid\nxx",
        household_checker__name=f"HH Checker {worker_id}",
        individual_checker__name=f"IND Checker  {worker_id}",
    )


@pytest.fixture
def household(program):
    from testutils.factories import CountryHouseholdFactory

    return CountryHouseholdFactory(batch__program=program, batch__country_office=program.country_office)


@pytest.mark.selenium
def test_login(selenium, user):
    selenium.get(f"{selenium.live_server.url}")
    selenium.find_by_css("input[name=username").send_keys(user.username)
    selenium.find_by_css("input[name=password").send_keys(user._password)
    selenium.find_by_css("button.primary").click()
    assert "You do not have any Office enabled." in selenium.page_source
