from _pytest.python_api import raises
from psutil import NoSuchProcess

from cloud_sql.cloud_sql_proxy import (
    run_cloud_sql_proxy,
    check_if_proxy_is_running,
    stop_cloud_sql_proxy,
    CloudProxyNotFoundError,
)
from tests import test_fixtures

from unittest import mock
from unittest.mock import MagicMock


class TestCloudSqlProxy:
    proxy_path = "/a/path"

    def test_run_proxy_no_path(self):
        with raises(CloudProxyNotFoundError):
            run_cloud_sql_proxy(
                None, test_fixtures.connection_name1, test_fixtures.port1, False
            )

    @mock.patch("cloud_sql.cloud_sql_proxy.subprocess.Popen")
    def test_run_proxy(self, popen_mock):
        pid = 123
        pid2 = 234
        mock_popen = MagicMock()
        mock_popen.pid = pid
        popen_mock.return_value = mock_popen
        returned_pid = run_cloud_sql_proxy(
            self.proxy_path, test_fixtures.connection_name1, test_fixtures.port1, False
        )
        assert returned_pid == pid
        popen_mock.assert_called_with(
            [
                "/a/path",
                f"-instances={test_fixtures.connection_name1}=tcp:{test_fixtures.port1}",
            ],
            start_new_session=True,
        )

        mock_popen.pid = pid2
        returned_pid2 = run_cloud_sql_proxy(
            self.proxy_path, test_fixtures.connection_name2, test_fixtures.port2, True
        )
        assert returned_pid2 == pid2
        popen_mock.assert_called_with(
            [
                "/a/path",
                "-enable_iam_login",
                f"-instances={test_fixtures.connection_name2}=tcp:{test_fixtures.port2}",
            ],
            start_new_session=True,
        )

    @mock.patch("cloud_sql.cloud_sql_proxy.psutil.Process")
    def test_is_running(self, mock_process):
        test_cmd_line = f"cloud_sql_proxy {test_fixtures.connection_name1}=tcp:1234"
        process_object = MagicMock()
        process_object.cmdline.return_value = [test_cmd_line]
        mock_process.return_value = process_object
        assert (
            check_if_proxy_is_running(123, test_fixtures.connection_name1) is not None
        )

        assert check_if_proxy_is_running(123, test_fixtures.connection_name2) is None

        mock_process.side_effect = NoSuchProcess(124)
        assert check_if_proxy_is_running(124, test_fixtures.connection_name1) is None

    @mock.patch("cloud_sql.cloud_sql_proxy.psutil.Process")
    def test_stop_proxy(self, mock_process):
        process_object = MagicMock()
        test_cmd_line = f"cloud_sql_proxy {test_fixtures.connection_name1}=tcp:1234"
        mock_process.return_value = process_object
        process_object.cmdline.return_value = [test_cmd_line]
        assert stop_cloud_sql_proxy(123, test_fixtures.connection_name1) is True
        process_object.kill.assert_called_once()
        assert stop_cloud_sql_proxy(123, test_fixtures.connection_name2) is False
        mock_process.side_effect = NoSuchProcess(124)
        assert stop_cloud_sql_proxy(124, test_fixtures.connection_name1) is False
