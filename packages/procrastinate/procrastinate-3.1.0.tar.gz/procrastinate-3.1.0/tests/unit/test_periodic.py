from __future__ import annotations

import itertools

import pytest

from procrastinate import exceptions, periodic


@pytest.fixture
def periodic_registry():
    return periodic.PeriodicRegistry()


@pytest.fixture
def periodic_deferrer(periodic_registry):
    return periodic.PeriodicDeferrer(registry=periodic_registry)


@pytest.fixture
def task(app):
    @app.task
    def foo(timestamp):
        pass

    return foo


@pytest.fixture
def cron_task(periodic_registry, task):
    def _(cron="0 0 * * *"):
        return periodic_registry.register_task(
            task=task, cron=cron, periodic_id="", configure_kwargs={}
        )

    return _


def test_register_task(periodic_registry, task):
    periodic_registry.register_task(
        task=task, cron="0 0 * * *", periodic_id="foo", configure_kwargs={}
    )

    assert periodic_registry.periodic_tasks == {
        (task.name, "foo"): periodic.PeriodicTask(
            task=task, cron="0 0 * * *", periodic_id="foo", configure_kwargs={}
        )
    }


def test_register_task_already_registered(periodic_registry, task):
    periodic_registry.register_task(
        task=task, cron="0 0 * * *", periodic_id="foo", configure_kwargs={}
    )
    with pytest.raises(exceptions.TaskAlreadyRegistered):
        periodic_registry.register_task(
            task=task, cron="0 0 * * *", periodic_id="foo", configure_kwargs={}
        )


def test_register_task_different_id(periodic_registry, task):
    periodic_registry.register_task(
        task=task, cron="0 0 * * *", periodic_id="foo", configure_kwargs={}
    )

    periodic_registry.register_task(
        task=task, cron="0 0 * * *", periodic_id="bar", configure_kwargs={}
    )
    assert len(periodic_registry.periodic_tasks) == 2


def test_schedule_decorator(periodic_registry, task):
    periodic_registry.periodic_decorator(cron="0 0 * * *", periodic_id="foo")(task)

    assert list(periodic_registry.periodic_tasks.values()) == [
        periodic.PeriodicTask(
            task=task, cron="0 0 * * *", periodic_id="foo", configure_kwargs={}
        )
    ]


@pytest.mark.parametrize(
    "cron, expected",
    [
        # ┌───────────── minute (0 - 59)
        # │ ┌───────────── hour (0 - 23)
        # │ │ ┌───────────── day of the month (1 - 31)
        # │ │ │ ┌───────────── month (1 - 12)
        # │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday;
        # │ │ │ │ │                                   7 is also Sunday on some systems)
        # │ │ │ │ │
        # │ │ │ │ │
        ("0 0 1 * *", 31 * 3600 * 24),
        ("0 0 * * *", 3600 * 24),
        ("0 * * * *", 3600),
        ("* * * * *", 60),
        ("* * * * * */5", 5),
    ],
)
def test_get_next_tick(periodic_deferrer, cron_task, cron, expected):
    cron_task(cron=cron)

    # Making things easier, we'll compute things next to timestamp 0
    assert periodic_deferrer.get_next_tick(at=0) == expected


def test_get_previous_tasks(periodic_deferrer, cron_task, task):
    cron_task(cron="* * * * *")

    assert list(periodic_deferrer.get_previous_tasks(at=3600 * 24 - 1)) == [
        (
            periodic.PeriodicTask(
                task=task, cron="* * * * *", periodic_id="", configure_kwargs={}
            ),
            3600 * 24 - 60,
        )
    ]


def test_get_timestamp_late(periodic_deferrer, cron_task):
    task = cron_task(cron="* * * * *")

    end = 3600 * 24
    timestamps = periodic_deferrer.get_timestamps(
        periodic_task=task, since=end - 4 * 60 + 1, until=end - 1
    )

    assert list(timestamps) == [end - 3 * 60, end - 2 * 60, end - 60]


def test_get_timestamp_no_timestamp(periodic_deferrer, cron_task):
    task = cron_task(cron="* * * * *")

    end = 3600 * 24
    timestamps = periodic_deferrer.get_timestamps(
        periodic_task=task, since=end - 30, until=end - 1
    )

    assert list(timestamps) == []


def test_get_timestamp_no_since_within_delay(periodic_deferrer, cron_task):
    task = cron_task(cron="* * * * *")

    end = 3600 * 24
    timestamps = periodic_deferrer.get_timestamps(
        periodic_task=task, since=None, until=end - 1
    )

    assert list(timestamps) == [end - 60]


def test_get_timestamp_no_since_not_within_delay(periodic_deferrer, cron_task, caplog):
    task = cron_task(cron="0 0 * * *")
    caplog.set_level("DEBUG")

    end = 3600 * 24
    timestamps = periodic_deferrer.get_timestamps(
        periodic_task=task, since=None, until=end - 1
    )

    assert list(timestamps) == []
    assert [r.action for r in caplog.records] == ["ignore_periodic_task"]


async def test_worker_no_task(periodic_deferrer, caplog):
    caplog.set_level("INFO")
    await periodic_deferrer.worker()

    assert [r.action for r in caplog.records] == ["periodic_deferrer_no_task"]


async def test_worker_loop(mocker, task):
    # The idea of this test is to make the inifite loop raise at some point
    mock = mocker.Mock()
    mock.wait_next_tick.side_effect = [None, None, ValueError]
    counter = itertools.count()

    class MockPeriodicDeferrer(periodic.PeriodicDeferrer):
        async def defer_jobs(self, jobs_to_defer):
            mock.defer_jobs()

        async def wait(self, next_tick):
            mock.wait_next_tick(next_tick)

        def get_next_tick(self, at):
            return next(counter)

    registry = periodic.PeriodicRegistry()
    registry.register_task(
        task=task, cron="* * * * *", periodic_id="", configure_kwargs={}
    )

    mock_deferrer = MockPeriodicDeferrer(registry=registry)
    with pytest.raises(ValueError):
        await mock_deferrer.worker()

    assert mock.mock_calls == [
        mocker.call.defer_jobs(),
        mocker.call.wait_next_tick(0),
        mocker.call.defer_jobs(),
        mocker.call.wait_next_tick(1),
        mocker.call.defer_jobs(),
        mocker.call.wait_next_tick(2),
    ]


async def test_wait_next_tick(periodic_deferrer, mocker):
    async def wait(val):
        assert val == 5 + periodic.MARGIN

    mocker.patch("asyncio.sleep", wait)

    await periodic_deferrer.wait(5)


async def test_defer_jobs(periodic_deferrer, task, connector, caplog):
    caplog.set_level("DEBUG")

    pt = periodic.PeriodicTask(
        task=task,
        cron="* * * * *",
        periodic_id="foo",
        configure_kwargs={
            "task_kwargs": {"a": "b"},
            "lock": "bar",
        },
    )
    await periodic_deferrer.defer_jobs([(pt, 1)])

    assert connector.queries == [
        (
            "defer_periodic_job",
            {
                "queue": "default",
                "args": {"timestamp": 1, "a": "b"},
                "defer_timestamp": 1,
                "lock": "bar",
                "queueing_lock": None,
                "task_name": task.name,
                "priority": 0,
                "periodic_id": "foo",
            },
        )
    ]
    assert [r.action for r in caplog.records] == ["periodic_task_deferred"]


async def test_defer_jobs_different_periodic_id(
    periodic_deferrer, task, connector, caplog
):
    caplog.set_level("DEBUG")
    connector.periodic_defers[(task.name, "foo")] = 1

    pt = periodic.PeriodicTask(
        task=task, cron="* * * * *", periodic_id="bar", configure_kwargs={}
    )

    await periodic_deferrer.defer_jobs([(pt, 1)])

    assert connector.queries == [
        (
            "defer_periodic_job",
            {
                "queue": "default",
                "args": {"timestamp": 1},
                "defer_timestamp": 1,
                "lock": None,
                "queueing_lock": None,
                "task_name": task.name,
                "priority": 0,
                "periodic_id": "bar",
            },
        )
    ]
    assert [r.action for r in caplog.records] == ["periodic_task_deferred"]


async def test_defer_jobs_already(periodic_deferrer, task, connector, caplog):
    caplog.set_level("DEBUG")
    connector.periodic_defers[(task.name, "foo")] = 1

    pt = periodic.PeriodicTask(
        task=task, cron="* * * * *", periodic_id="foo", configure_kwargs={}
    )

    await periodic_deferrer.defer_jobs([(pt, 1)])

    assert connector.queries == [
        (
            "defer_periodic_job",
            {
                "queue": "default",
                "args": {"timestamp": 1},
                "defer_timestamp": 1,
                "lock": None,
                "queueing_lock": None,
                "task_name": task.name,
                "priority": 0,
                "periodic_id": "foo",
            },
        )
    ]
    assert [r.action for r in caplog.records] == ["periodic_task_already_deferred"]


async def test_defer_jobs_queueing_lock(periodic_deferrer, task, caplog):
    caplog.set_level("DEBUG")

    pt1 = periodic.PeriodicTask(
        task=task,
        cron="* * * * *",
        periodic_id="foo",
        configure_kwargs={"queueing_lock": "bar"},
    )

    pt2 = periodic.PeriodicTask(
        task=task,
        cron="* * * * *",
        periodic_id="foo",
        configure_kwargs={"queueing_lock": "bar"},
    )

    caplog.clear()
    await periodic_deferrer.defer_jobs([(pt1, 1), (pt2, 2)])

    assert [r.action for r in caplog.records] == [
        "periodic_task_deferred",
        "skip_periodic_task_queueing_lock",
    ]
