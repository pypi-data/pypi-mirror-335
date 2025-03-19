from unittest import mock
from unittest.mock import patch, mock_open

import jsonpickle

from cloud_sql.config import Configuration
from cloud_sql.instances import Site
from cloud_sql.persistence import Persistence, default_base_path
from cloud_sql.running_instances import RunningInstances
from tests import test_fixtures


class TestPersistence:
    @mock.patch("cloud_sql.persistence.os.makedirs")
    @mock.patch("cloud_sql.persistence.os.path.exists")
    def test_save_site(self, mock_path, mock_makedirs):
        mock_path.return_value = True

        with patch("builtins.open", new_callable=mock_open()) as open_mock:
            persistence = Persistence("test1")
            persistence.save_site(test_fixtures.site1)
            mock_makedirs.assert_not_called()
            open_mock.assert_called_with("test1/instances.json", "w")
            f = open_mock().__enter__()
            f.write.assert_called_once()
            callargs = f.write.call_args[0][0]
            actual_site: Site = jsonpickle.decode(callargs)
            assert len(actual_site.instances) == len(test_fixtures.site1.instances)

        mock_path.return_value = False

        with patch("builtins.open", new_callable=mock_open()) as open_mock:
            persistence = Persistence("test1")
            persistence.save_site(test_fixtures.site1)
            mock_makedirs.assert_called_once_with("test1")
            open_mock.assert_called_with("test1/instances.json", "w")
            f = open_mock().__enter__()
            f.write.assert_called_once()
            callargs = f.write.call_args[0][0]
            actual_site: Site = jsonpickle.decode(callargs)
            assert len(actual_site.instances) == len(test_fixtures.site1.instances)

    @mock.patch("cloud_sql.persistence.os.path.exists")
    def test_load_site(self, mock_path):
        mock_path.return_value = True

        json_str = jsonpickle.encode(test_fixtures.site1)
        with patch("builtins.open", new_callable=mock_open()) as open_mock:
            persistence = Persistence("test1")
            open_mock().__enter__().read.return_value = json_str
            actual_site = persistence.load_site()
            open_mock.assert_called_with("test1/instances.json", "r")
            assert len(actual_site.instances) == len(test_fixtures.site1.instances)

        mock_path.return_value = False
        assert len(persistence.load_site().instances) == 0

    @mock.patch("cloud_sql.persistence.os.makedirs")
    @mock.patch("cloud_sql.persistence.os.path.exists")
    def test_save_config(self, mock_path, mock_makedirs):
        mock_path.return_value = True

        with patch("builtins.open", new_callable=mock_open()) as open_mock:
            persistence = Persistence("test1")
            persistence.save_config(test_fixtures.config1)
            mock_makedirs.assert_not_called()
            open_mock.assert_called_with("test1/config.json", "w")
            f = open_mock().__enter__()
            f.write.assert_called_once()
            callargs = f.write.call_args[0][0]
            actual_config: Configuration = jsonpickle.decode(callargs)
            assert actual_config.cloud_sql_path == test_fixtures.config1.cloud_sql_path

        mock_path.return_value = False

        with patch("builtins.open", new_callable=mock_open()) as open_mock:
            persistence = Persistence("test1")
            persistence.save_config(test_fixtures.config1)
            mock_makedirs.assert_called_once_with("test1")
            open_mock.assert_called_with("test1/config.json", "w")
            f = open_mock().__enter__()
            f.write.assert_called_once()
            callargs = f.write.call_args[0][0]
            actual_config: Configuration = jsonpickle.decode(callargs)
            assert actual_config.cloud_sql_path == test_fixtures.config1.cloud_sql_path

    @mock.patch("cloud_sql.config.shutil.which")
    @mock.patch("cloud_sql.persistence.os.path.exists")
    def test_load_config(self, mock_path, mock_which):
        mock_path.return_value = True

        json_str = jsonpickle.encode(test_fixtures.config1)
        with patch("builtins.open", new_callable=mock_open()) as open_mock:
            persistence = Persistence("test1")
            open_mock().__enter__().read.return_value = json_str
            actual_config = persistence.load_config()
            open_mock.assert_called_with("test1/config.json", "r")
            assert actual_config.cloud_sql_path == test_fixtures.config1.cloud_sql_path

        mock_path.return_value = False
        mock_which.return_value = "/default/cloud_proxy"
        assert persistence.load_config().cloud_sql_path == "/default/cloud_proxy"

    @mock.patch("cloud_sql.persistence.os.makedirs")
    @mock.patch("cloud_sql.persistence.os.path.exists")
    def test_save_running_instances(self, mock_path, mock_makedirs):
        mock_path.return_value = True

        with patch("builtins.open", new_callable=mock_open()) as open_mock:
            persistence = Persistence("test1")
            persistence.save_running(test_fixtures.running_instances1)
            mock_makedirs.assert_not_called()
            open_mock.assert_called_with("test1/running.json", "w")
            f = open_mock().__enter__()
            f.write.assert_called_once()
            callargs = f.write.call_args[0][0]
            actual_running: RunningInstances = jsonpickle.decode(callargs)
            assert len(actual_running.instances) == len(
                test_fixtures.running_instances1.instances
            )

        mock_path.return_value = False
        with patch("builtins.open", new_callable=mock_open()) as open_mock:
            persistence = Persistence("test1")
            persistence.save_running(test_fixtures.running_instances1)
            mock_makedirs.assert_called_once_with("test1")
            open_mock.assert_called_with("test1/running.json", "w")
            f = open_mock().__enter__()
            f.write.assert_called_once()
            callargs = f.write.call_args[0][0]
            actual_running: RunningInstances = jsonpickle.decode(callargs)
            assert len(actual_running.instances) == len(
                test_fixtures.running_instances1.instances
            )

    @mock.patch("cloud_sql.persistence.os.path.exists")
    def test_load_running_instances(self, mock_path):
        mock_path.return_value = True

        json_str = jsonpickle.encode(test_fixtures.running_instances1)
        with patch("builtins.open", new_callable=mock_open()) as open_mock:
            persistence = Persistence("test1")
            open_mock().__enter__().read.return_value = json_str
            actual_running = persistence.load_running()
            open_mock.assert_called_with("test1/running.json", "r")
            assert len(actual_running.instances) == len(
                test_fixtures.running_instances1.instances
            )
        mock_path.return_value = False
        assert len(persistence.load_running().instances) == 0

    @mock.patch("cloud_sql.persistence.os.getenv")
    def test_default_base_path(self, mock_getenv):
        mock_getenv.return_value = "/home/test"
        assert default_base_path() == "/home/test/.cloudsql"
        mock_getenv.assert_called_once_with("HOME")
