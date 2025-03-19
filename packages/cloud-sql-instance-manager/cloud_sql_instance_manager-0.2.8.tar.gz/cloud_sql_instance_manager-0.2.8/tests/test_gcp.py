from cloud_sql.config import Configuration
from cloud_sql.gcp import obtain_instances
from cloud_sql.instances import Site
from tests import test_fixtures

from unittest import mock
from unittest.mock import MagicMock


class TestGcp:
    proxy_path = "/a/path"
    test_response = {
        "items": [
            {
                "name": test_fixtures.name1,
                "region": test_fixtures.region1,
                "project": test_fixtures.project1,
                "connectionName": test_fixtures.connection_name1,
                "instanceType": "CLOUD_SQL_INSTANCE",
            },
            {
                "name": "wrong",
                "region": "wrong",
                "project": test_fixtures.project1,
                "connectionName": "wrong",
                "instanceType": "OTHER",
            },
        ]
    }

    @mock.patch("cloud_sql.gcp.discovery.build")
    @mock.patch("cloud_sql.gcp.google.auth.default")
    def test_obtain_instances(self, mock_auth, mock_discovery):
        service = MagicMock()
        instances = MagicMock()
        request = MagicMock()
        config = MagicMock(spec=Configuration)
        config.enable_iam_by_default = True
        mock_auth.return_value = "creds1", test_fixtures.project1
        mock_discovery.return_value = service
        service.instances.return_value = instances
        instances.list.return_value = request
        request.execute.return_value = self.test_response
        site = Site({})
        obtain_instances(config, site, None, None)
        assert len(site.instances) == 1
        assert site.instances[test_fixtures.connection_name1].iam is True
        assert "database-postgres" in site.nicknames

        instances.list.reset_mock()
        obtain_instances(config, site, "override", None)
        instances.list.assert_called_once_with(project="override")

    @mock.patch("cloud_sql.gcp.discovery.build")
    @mock.patch("cloud_sql.gcp.google.auth.default")
    def test_obtain_instances_2(self, mock_auth, mock_discovery):
        service = MagicMock()
        instances = MagicMock()
        request = MagicMock()
        config = MagicMock(spec=Configuration)
        config.enable_iam_by_default = True
        mock_auth.return_value = "creds1", test_fixtures.project1
        mock_discovery.return_value = service
        service.instances.return_value = instances
        instances.list.return_value = request
        request.execute.return_value = self.test_response
        site = Site({test_fixtures.connection_name3: test_fixtures.instance3})
        obtain_instances(config, site, None, True)
        assert len(site.instances) == 1
        assert site.instances[test_fixtures.connection_name1].iam is True
        assert "database-postgres" in site.nicknames

        instances.list.reset_mock()