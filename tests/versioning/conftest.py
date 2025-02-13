from pathlib import Path

import pytest

from country_workspace import VERSION


@pytest.fixture
def test_scripts_folder():
    return Path(__file__).parent / "scripts"


@pytest.fixture
def scripts(test_scripts_folder):
    return [
        (test_scripts_folder / "0001_t.py"),
        (test_scripts_folder / "0002_t.py"),
        (test_scripts_folder / "0003_t.py"),
    ]


@pytest.fixture
def version1(test_scripts_folder):
    from testutils.factories import ScriptFactory

    f = test_scripts_folder / "0001_t.py"
    return ScriptFactory(name=f.name, version=VERSION)


@pytest.fixture
def version2(test_scripts_folder):
    from testutils.factories import ScriptFactory

    f = test_scripts_folder / "0002_t.py"
    return ScriptFactory(name=f.name, version=VERSION)


@pytest.fixture
def version3(test_scripts_folder):
    from testutils.factories import ScriptFactory

    f = test_scripts_folder / "0003_t.py"
    return ScriptFactory(name=f.name, version=VERSION)


@pytest.fixture
def manager(test_scripts_folder):
    from country_workspace.versioning.management.manager import Manager

    return Manager(test_scripts_folder)
