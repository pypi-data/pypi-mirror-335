from unittest import mock

from _pytest.python_api import raises

from cloud_sql.config import default_configuration, Configuration, PathNotFoundError
from cloud_sql.running_instances import RunningInstances
from tests import test_fixtures


class TestRunningInstances:
    def test_add_running(self):
        running_instances = RunningInstances({})
        running_instances.add_running(
            test_fixtures.pid1, test_fixtures.connection_name1
        )
        assert (
            running_instances.instances[test_fixtures.connection_name1]
            == test_fixtures.pid1
        )

        running_instances.add_running(
            test_fixtures.pid2, test_fixtures.connection_name1
        )
        assert (
            running_instances.instances[test_fixtures.connection_name1]
            == test_fixtures.pid2
        )

    def test_remove_running(self):
        running_instances = RunningInstances(
            {test_fixtures.connection_name1: test_fixtures.pid1}
        )
        running_instances.remove_running(test_fixtures.connection_name1)
        assert len(running_instances.instances) == 0

    def test_get_running(self):
        running_instances = RunningInstances(
            {test_fixtures.connection_name1: test_fixtures.pid1}
        )
        assert (
            running_instances.get_running(test_fixtures.connection_name1)
            == test_fixtures.pid1
        )
        assert running_instances.get_running(test_fixtures.connection_name2) is None

    def test_get_all_running(self):
        running_instances = RunningInstances(
            {test_fixtures.connection_name1: test_fixtures.pid1}
        )
        assert len(running_instances.get_all_running()) == 1
