import os

import pytest


def requires_env(*envs):
    missing = [env for env in envs if env not in os.environ]
    return pytest.mark.skipif(len(missing) > 0, reason=f"Not suitable environment {missing} for current test")
