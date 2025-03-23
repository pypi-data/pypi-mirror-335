from __future__ import annotations

import os
import subprocess

import pytest

APP_MODULE = "tests.acceptance.app"


@pytest.fixture
def process_env(connection_params):
    def _(*, app="app"):
        env = os.environ.copy()
        env.update(
            {
                "PROCRASTINATE_APP": f"{APP_MODULE}.{app}",
                "PROCRASTINATE_VERBOSE": "3",
                "PROCRASTINATE_DEFER_UNKNOWN": "True",
                "PGDATABASE": connection_params["dbname"],
                "PYTHONUNBUFFERED": "1",
            }
        )
        return env

    return _


@pytest.fixture
def defer(process_env):
    from .app import json_dumps

    def func(task_name, args=None, app="app", **kwargs):
        args = args or []
        full_task_name = f"{APP_MODULE}.{task_name}"
        subprocess.check_output(
            ["procrastinate", "defer", full_task_name, json_dumps(kwargs), *args],
            env=process_env(app=app),
        )

    return func
