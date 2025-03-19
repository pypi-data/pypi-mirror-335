from unittest import mock
from unittest.mock import MagicMock, call, patch

from cloud_sql.config import Configuration, PathNotFoundError
from cloud_sql.instance_manager import (
    refresh_running,
    get_instance_from_nick,
    print_list,
    print_list_running,
    start,
    stop,
    import_instances,
    update,
    update_config,
    execute_command,
    add_instance,
    remove_instance,
)
from cloud_sql.instances import (
    Site,
    Instance,
    InstanceNotFoundError,
    InvalidConnectionName,
    DuplicateInstanceError,
)
from cloud_sql.running_instances import RunningInstances
from tests import test_fixtures


def add_instance_side_effect(*args):
    instance = MagicMock(spec=Instance)
    instance.port = test_fixtures.port1
    instance.iam = False
    instance.connection_name = test_fixtures.connection_name1
    instance.name = test_fixtures.name1
    instance.nick_name = "nick"
    instance.project = test_fixtures.project1
    args[1].instances = {test_fixtures.connection_name1: instance}
    return (1,0)


class TestInstanceManager:
    @patch("cloud_sql.instance_manager.check_if_proxy_is_running")
    def test_refresh_running(self, mock_check_proxy):
        running_instances = MagicMock(spec=RunningInstances)
        running_instances.get_all_running.return_value = {
            test_fixtures.connection_name1: test_fixtures.pid1,
            test_fixtures.connection_name2: test_fixtures.pid2,
        }

        mock_check_proxy.side_effect = (
            lambda p, cn: MagicMock() if cn == test_fixtures.connection_name1 else None
        )
        refresh_running(running_instances)
        running_instances.remove_running.assert_called_once_with(
            test_fixtures.connection_name2
        )

    @mock.patch("cloud_sql.instance_manager.print")
    def test_get_instance_from_nick(self, mock_print):
        site = MagicMock(spec=Site)
        instance = MagicMock(spec=Instance)
        site.get_instance_by_nick_name.return_value = instance
        assert get_instance_from_nick(site, "nick", None) == instance
        site.get_instance_by_nick_name.assert_called_once_with("nick", None)
        site.get_instance_by_nick_name.return_value = None
        site.get_instance_by_nick_name.side_effect = InstanceNotFoundError
        assert get_instance_from_nick(site, "nick1", None) is None
        mock_print.assert_called_once_with("No instance with that name or nick found.")
        site.get_instance_by_nick_name.side_effect = DuplicateInstanceError
        mock_print.reset_mock()
        assert get_instance_from_nick(site, "nick2", None) is None
        mock_print.assert_called_once_with(
            "More than one instance with that name or nick found, try specifying a project with --project."
        )

    @mock.patch("cloud_sql.instance_manager.print")
    def test_print_list(self, mock_print):
        test_print = ["one", "two"]
        site = MagicMock(spec=Site)
        site.print_list.return_value = test_print
        print_list(site, "proj")
        site.print_list.assert_called_once_with("proj")
        assert mock_print.call_count == 2

    @mock.patch("cloud_sql.instance_manager.print")
    def test_print_running(self, mock_print):
        running_instances = MagicMock(spec=RunningInstances)
        running_instances.get_all_running.return_value = {
            test_fixtures.connection_name1: test_fixtures.pid1
        }
        instance = MagicMock(spec=Instance)
        instance.print.return_value = "TestInstance"
        site = MagicMock(spec=Site)
        site.instances = {test_fixtures.connection_name1: instance}

        print_list_running(site, running_instances)
        instance.print.assert_called_once_with(test_fixtures.pid1)
        mock_print.assert_called_once_with("TestInstance")

        mock_print.reset_mock()
        running_instances.get_all_running.return_value = {}
        print_list_running(site, running_instances)
        mock_print.assert_called_once_with("No running instances")

    @mock.patch("cloud_sql.instance_manager.get_instance_from_nick")
    @mock.patch("cloud_sql.instance_manager.run_cloud_sql_proxy")
    @mock.patch("cloud_sql.instance_manager.print")
    def test_start(self, mock_print, mock_run, mock_get_from_nick):
        config = MagicMock(spec=Configuration)
        config.cloud_sql_path = "/cloud/sql"

        instance = MagicMock(spec=Instance)
        instance.port = test_fixtures.port1
        instance.iam = False
        instance.connection_name = test_fixtures.connection_name1
        instance.name = test_fixtures.name1
        instance.nick_name = "nick"

        site = MagicMock(spec=Site)
        site.instances = {test_fixtures.connection_name1: instance}
        site.get_default_instances.return_value = [instance]

        running_instances = MagicMock(spec=RunningInstances)
        running_instances.get_running.return_value = None

        start(config, site, running_instances, "default", test_fixtures.project1)

        mock_run.assert_called_once_with(
            "/cloud/sql", test_fixtures.connection_name1, test_fixtures.port1, False
        )
        mock_print.assert_called_once_with(
            f"Started {test_fixtures.name1} on port {test_fixtures.port1}"
        )

        mock_run.reset_mock()
        mock_print.reset_mock()
        mock_get_from_nick.return_value = instance
        site.get_default_instances.return_value = []
        start(config, site, running_instances, "default", test_fixtures.project1)
        mock_print.assert_called_once_with("No default instances found")

        mock_run.reset_mock()
        mock_print.reset_mock()
        site.get_default_instances.return_value = []

        start(config, site, running_instances, "nick", test_fixtures.project1)

        mock_get_from_nick.assert_called_once_with(site, "nick", test_fixtures.project1)
        mock_run.assert_called_once_with(
            "/cloud/sql", test_fixtures.connection_name1, test_fixtures.port1, False
        )
        mock_print.assert_called_once_with(
            f"Started {test_fixtures.name1} on port {test_fixtures.port1}"
        )

        mock_run.reset_mock()
        mock_print.reset_mock()
        mock_get_from_nick.reset_mock()

        mock_get_from_nick.return_value = instance
        running_instances.get_running.return_value = {
            test_fixtures.connection_name1: test_fixtures.pid1
        }

        start(config, site, running_instances, "nick", test_fixtures.project1)

        mock_get_from_nick.assert_called_once_with(site, "nick", test_fixtures.project1)
        mock_run.assert_not_called()
        mock_print.assert_called_once_with("nick is already running.")

        mock_run.reset_mock()
        mock_print.reset_mock()
        mock_get_from_nick.reset_mock()

        mock_get_from_nick.return_value = None

        start(config, site, running_instances, "nick", test_fixtures.project1)

        mock_get_from_nick.assert_called_once_with(site, "nick", test_fixtures.project1)
        mock_run.assert_not_called()

    @mock.patch("cloud_sql.instance_manager.get_instance_from_nick")
    @mock.patch("cloud_sql.instance_manager.stop_cloud_sql_proxy")
    @mock.patch("cloud_sql.instance_manager.print")
    def test_stop(self, mock_print, mock_stop, mock_get_from_nick):
        running_instances = MagicMock(spec=RunningInstances)
        running_instances.get_all_running.return_value = {}

        instance = MagicMock(spec=Instance)
        instance.port = test_fixtures.port1
        instance.iam = False
        instance.connection_name = test_fixtures.connection_name1
        instance.name = test_fixtures.name1
        instance.nick_name = "nick"
        instance.project = test_fixtures.project1

        site = MagicMock(spec=Site)
        site.instances = {test_fixtures.connection_name1: instance}

        stop(site, running_instances, "all", test_fixtures.project1)
        mock_print.assert_called_once_with("No running instances found")
        mock_stop.assert_not_called()

        mock_print.reset_mock()

        running_instances.get_all_running.return_value = {
            test_fixtures.connection_name1: test_fixtures.pid1
        }
        running_instances.get_running.return_value = test_fixtures.pid1
        mock_stop.return_value = True
        stop(site, running_instances, "all", test_fixtures.project1)
        mock_print.assert_called_once_with(
            f"Stopped {test_fixtures.name1} on port {test_fixtures.port1}"
        )
        mock_stop.assert_called_once_with(
            test_fixtures.pid1, test_fixtures.connection_name1
        )
        running_instances.remove_running.assert_called_once_with(
            test_fixtures.connection_name1
        )
        running_instances.get_running.assert_called_once_with(
            test_fixtures.connection_name1
        )

        mock_print.reset_mock()
        mock_stop.reset_mock()
        running_instances.remove_running.reset_mock()
        running_instances.get_running.reset_mock()

        running_instances.get_all_running.return_value = {
            test_fixtures.connection_name1: test_fixtures.pid1
        }
        running_instances.get_running.return_value = test_fixtures.pid1
        mock_get_from_nick.return_value = instance
        mock_stop.return_value = True
        stop(site, running_instances, "nick", test_fixtures.project1)
        mock_get_from_nick.assert_called_once_with(site, "nick", test_fixtures.project1)
        mock_print.assert_called_once_with(
            f"Stopped {test_fixtures.name1} on port {test_fixtures.port1}"
        )
        mock_stop.assert_called_once_with(
            test_fixtures.pid1, test_fixtures.connection_name1
        )
        running_instances.remove_running.assert_called_once_with(
            test_fixtures.connection_name1
        )
        running_instances.get_running.assert_called_once_with(
            test_fixtures.connection_name1
        )

        mock_print.reset_mock()
        mock_stop.reset_mock()
        running_instances.remove_running.reset_mock()
        running_instances.get_running.reset_mock()
        mock_get_from_nick.reset_mock()

        running_instances.get_all_running.return_value = {
            test_fixtures.connection_name1: test_fixtures.pid1
        }
        running_instances.get_running.return_value = test_fixtures.pid1
        mock_get_from_nick.return_value = instance
        mock_stop.return_value = False
        stop(site, running_instances, "nick", test_fixtures.project1)
        mock_get_from_nick.assert_called_once_with(site, "nick", test_fixtures.project1)
        mock_print.assert_called_once_with(
            "Could not locate process to stop for nick, it has been removed from the running list"
        )
        mock_stop.assert_called_once_with(
            test_fixtures.pid1, test_fixtures.connection_name1
        )
        running_instances.remove_running.assert_called_once_with(
            test_fixtures.connection_name1
        )
        running_instances.get_running.assert_called_once_with(
            test_fixtures.connection_name1
        )

        mock_print.reset_mock()
        mock_stop.reset_mock()
        running_instances.remove_running.reset_mock()
        running_instances.get_running.reset_mock()
        mock_get_from_nick.reset_mock()

        running_instances.get_running.return_value = None
        mock_get_from_nick.return_value = instance
        mock_stop.return_value = False
        stop(site, running_instances, "nick", test_fixtures.project1)
        mock_get_from_nick.assert_called_once_with(site, "nick", test_fixtures.project1)
        mock_print.assert_called_once_with("nick is not running")
        mock_stop.assert_not_called()
        running_instances.remove_running.assert_not_called()
        running_instances.get_running.assert_called_once_with(
            test_fixtures.connection_name1
        )

        running_instances.reset_mock()
        mock_print.reset_mock()
        mock_get_from_nick.reset_mock()

        mock_get_from_nick.return_value = None

        stop(site, running_instances, "nick", test_fixtures.project1)
        mock_get_from_nick.assert_called_once_with(site, "nick", test_fixtures.project1)
        mock_stop.assert_not_called()

    @mock.patch("cloud_sql.instance_manager.obtain_instances")
    @mock.patch("cloud_sql.instance_manager.print")
    def test_import_instances(self, mock_print, mock_obtain_instances):
        site = MagicMock(spec=Site)
        site.instances = {}

        config = MagicMock(spec=Configuration)
        mock_obtain_instances.side_effect = add_instance_side_effect
        import_instances(config, site, test_fixtures.project1, True)
        mock_obtain_instances.assert_called_once_with(
            config, site, test_fixtures.project1, True
        )
        mock_print.assert_has_calls([call("Imported 1 instances."),call("Removed 0 instances.")])

    @mock.patch("cloud_sql.instance_manager.get_instance_from_nick")
    @mock.patch("cloud_sql.instance_manager.print")
    def test_update(self, mock_print, mock_get_from_nick):
        instance = MagicMock(spec=Instance)
        instance.port = test_fixtures.port1
        instance.iam = False
        instance.connection_name = test_fixtures.connection_name1
        instance.name = test_fixtures.name1
        instance.nick_name = "nick"
        instance.project = test_fixtures.project1

        site = MagicMock(spec=Site)
        site.instances = {test_fixtures.connection_name1: instance}
        site.get_instance_by_nick_name.side_effect = InstanceNotFoundError

        mock_get_from_nick.return_value = instance
        instance.print.return_value = "instance"
        update(site, "nick", test_fixtures.project1, "True", "newnick", "True")
        instance.set_iam.assert_called_once_with(True)
        instance.set_default.assert_called_once_with(True)
        assert instance.nick_name == "newnick"
        site.set_up_nicknames.assert_called_once()
        mock_print.assert_any_call("Instance updated:")
        mock_print.assert_any_call("instance")

        site.get_instance_by_nick_name.reset_mock()
        site.get_instance_by_nick_name.side_effect = None
        site.set_up_nicknames.reset_mock()
        site.get_instance_by_nick_name.return_value = MagicMock(spec=Instance)
        instance.nick_name = "oldnick"
        mock_print.reset_mock()

        mock_get_from_nick.return_value = instance
        instance.print.return_value = "instance"

        update(site, "nick", test_fixtures.project1, None, "newnick", None)
        assert instance.nick_name == "oldnick"
        site.set_up_nicknames.assert_not_called()
        mock_print.assert_any_call("That nick would not be unique, pick another.")
        mock_print.assert_any_call("Instance updated:")
        mock_print.assert_any_call("instance")

    @mock.patch("cloud_sql.instance_manager.print")
    def test_update_config(self, mock_print):
        config = MagicMock(spec=Configuration)
        config.print.return_value = "printed config"
        update_config(config, None, None)
        mock_print.assert_called_once_with("printed config")
        mock_print.reset_mock()

        update_config(config, "/new/path", None)
        config.new_path.assert_called_once_with("/new/path")
        config.set_enable_iam_by_default.assert_not_called()
        mock_print.assert_called_once_with("Updated cloud_sql_proxy path to /new/path")
        mock_print.reset_mock()
        config.new_path.reset_mock()

        config.new_path.side_effect = PathNotFoundError
        update_config(config, "/new/path", None)
        config.new_path.assert_called_once_with("/new/path")
        mock_print.assert_called_once_with(
            "That file appears not to exist. It needs to be the fully qualified path."
        )
        mock_print.reset_mock()
        config.new_path.reset_mock()
        config.enable_iam_by_default = True
        update_config(config, None, "true")
        config.new_path.assert_not_called()
        config.set_enable_iam_by_default.assert_called_once_with(True)
        mock_print.assert_called_once_with("Updated default IAM setting to: True")

    @mock.patch("cloud_sql.instance_manager.print")
    def test_add(self, mock_print):
        config = MagicMock(spec=Configuration)
        config.enable_iam_by_default = True

        instance = MagicMock(spec=Instance)
        instance.port = test_fixtures.port1
        instance.iam = False
        instance.connection_name = test_fixtures.connection_name1
        instance.name = test_fixtures.name1
        instance.nick_name = "nick"
        instance.project = test_fixtures.project1
        instance.print.return_value = "conn print"

        site = MagicMock(spec=Site)
        site.add_instance.return_value = instance

        add_instance(config, site, test_fixtures.connection_name1, "nick1")
        site.add_instance.assert_called_once_with(
            test_fixtures.connection_name1, "nick1", True
        )
        mock_print.assert_any_call("Added new instance")
        mock_print.assert_any_call("conn print")

        site.add_instance.reset_mock()
        site.add_instance.side_effect = InvalidConnectionName("invalid!")
        add_instance(config, site, test_fixtures.connection_name1, "nick1")
        site.add_instance.assert_called_once_with(
            test_fixtures.connection_name1, "nick1", True
        )
        mock_print.assert_any_call("invalid!")

        site.add_instance.reset_mock()
        site.add_instance.side_effect = DuplicateInstanceError("duplicate!!")
        add_instance(config, site, test_fixtures.connection_name1, "nick1")
        site.add_instance.assert_called_once_with(
            test_fixtures.connection_name1, "nick1", True
        )
        mock_print.assert_any_call("duplicate!!")

    @mock.patch("cloud_sql.instance_manager.stop")
    @mock.patch("cloud_sql.instance_manager.get_instance_from_nick")
    @mock.patch("cloud_sql.instance_manager.print")
    def test_remove(self, mock_print, mock_get_from_nick, mock_stop):
        instance = MagicMock(spec=Instance)
        instance.port = test_fixtures.port1
        instance.iam = False
        instance.connection_name = test_fixtures.connection_name1
        instance.name = test_fixtures.name1
        instance.nick_name = "nick"
        instance.project = test_fixtures.project1

        running_instances = MagicMock(spec=RunningInstances)
        running_instances.instances = {test_fixtures.connection_name1: instance}

        site = MagicMock(spec=Site)
        site.remove_instance.return_value = True
        site.instances = {test_fixtures.connection_name1: instance}
        site.get_default_instances.return_value = [instance]

        mock_get_from_nick.return_value = instance

        remove_instance(
            site, running_instances, test_fixtures.name1, test_fixtures.project1
        )
        site.remove_instance.assert_called_once_with(test_fixtures.connection_name1)
        mock_print.assert_any_call(
            f"Removed connection: {test_fixtures.connection_name1}"
        )
        mock_stop.assert_called_once_with(site, "nick", test_fixtures.project1)

    @mock.patch("cloud_sql.instance_manager.remove_instance")
    @mock.patch("cloud_sql.instance_manager.add_instance")
    @mock.patch("cloud_sql.instance_manager.print_list")
    @mock.patch("cloud_sql.instance_manager.print_list_running")
    @mock.patch("cloud_sql.instance_manager.start")
    @mock.patch("cloud_sql.instance_manager.stop")
    @mock.patch("cloud_sql.instance_manager.update")
    @mock.patch("cloud_sql.instance_manager.import_instances")
    @mock.patch("cloud_sql.instance_manager.update_config")
    @mock.patch("cloud_sql.instance_manager.print")
    def test_command(
        self,
        mock_print,
        mock_update_config,
        mock_import_instances,
        mock_update,
        mock_stop,
        mock_start,
        mock_list_running,
        mock_print_list,
        mock_add_instance,
        mock_remove_instance,
    ):
        config = MagicMock(spec=Configuration)
        site = MagicMock(spec=Site)
        running_instances = MagicMock(spec=RunningInstances)

        parameters = {"command": "list", "project": test_fixtures.project1}
        execute_command(parameters, config, site, running_instances)
        mock_print_list.assert_called_once_with(site, test_fixtures.project1)

        parameters = {"command": "list-running"}
        execute_command(parameters, config, site, running_instances)
        mock_list_running.assert_called_once_with(site, running_instances)

        parameters = {
            "command": "start",
            "name": "nick",
            "project": test_fixtures.project1,
        }
        execute_command(parameters, config, site, running_instances)
        mock_start.assert_called_once_with(
            config, site, running_instances, "nick", test_fixtures.project1
        )

        parameters = {
            "command": "stop",
            "name": "nick",
            "project": test_fixtures.project1,
        }
        execute_command(parameters, config, site, running_instances)
        mock_stop.assert_called_once_with(
            site, running_instances, "nick", test_fixtures.project1
        )

        parameters = {
            "command": "update",
            "name": "nick",
            "project": test_fixtures.project1,
            "iam": "true",
            "nick": "newnick",
            "default": "false",
        }
        execute_command(parameters, config, site, running_instances)
        mock_update.assert_called_once_with(
            site, "nick", test_fixtures.project1, "true", "newnick", "false"
        )

        parameters = {"command": "import", "project": test_fixtures.project1, "tidy": True}
        execute_command(parameters, config, site, running_instances)
        mock_import_instances.assert_called_once_with(
            config, site, test_fixtures.project1, True
        )

        parameters = {"command": "config", "path": "/test/path", "iam_default": "true"}
        execute_command(parameters, config, site, running_instances)
        mock_update_config.assert_called_once_with(config, "/test/path", "true")

        parameters = {
            "command": "add",
            "connection_name": "project:region:name",
            "nick": "newnick",
        }
        execute_command(parameters, config, site, running_instances)
        mock_add_instance.assert_called_once_with(
            config, site, "project:region:name", "newnick"
        )

        parameters = {"command": "remove", "name": "nick", "project": "project"}
        execute_command(parameters, config, site, running_instances)
        mock_remove_instance.assert_called_once_with(
            site, running_instances, "nick", "project"
        )

        parameters = {"command": "fish"}
        execute_command(parameters, config, site, running_instances)
        mock_print.assert_called_once_with(
            "Specify a command or ask for help with --help"
        )
