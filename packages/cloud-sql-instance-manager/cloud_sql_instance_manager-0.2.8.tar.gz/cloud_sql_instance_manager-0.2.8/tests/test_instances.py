from _pytest.python_api import raises

from cloud_sql.instances import (
    Instance,
    Site,
    InstanceNotFoundError,
    DuplicateInstanceError,
    InvalidConnectionName,
)
from tests import test_fixtures


class TestInstance:
    # name = 'database-postgres-instance-1234'
    # project = 'project-1'
    # region = 'region-1'
    # connection_name = f'{project}:{region}:{name}'
    # port = 5111

    def test_default_nick_name(self):
        instance = Instance(
            test_fixtures.name1,
            test_fixtures.region1,
            test_fixtures.project1,
            test_fixtures.connection_name1,
            False,
        )
        assert instance.nick_name == "database-postgres"

    def test_assign_port(self):
        instance = Instance(
            test_fixtures.name1,
            test_fixtures.region1,
            test_fixtures.project1,
            test_fixtures.connection_name1,
            False,
        )
        instance.assign_port(test_fixtures.port1)
        assert instance.port == 5511

    def test_print(self):
        instance = Instance(
            test_fixtures.name1,
            test_fixtures.region1,
            test_fixtures.project1,
            test_fixtures.connection_name1,
            False,
        )
        instance.assign_port(test_fixtures.port1)
        no_pid = instance.print(None)
        pid = instance.print(4512)
        assert (
            no_pid
            == "Project: project-1, Nick: database-postgres, Port 5511, Name: database-postgres-instance-1234, Region: region-1, IAM Enabled: False, Default: False"
        )
        assert pid == f"Pid: 4512, {no_pid}"

    def test_set_iam(self):
        instance = Instance(
            test_fixtures.name1,
            test_fixtures.region1,
            test_fixtures.project1,
            test_fixtures.connection_name1,
            False,
        )
        assert instance.iam is False
        instance.set_iam(True)
        assert instance.iam is True

    def test_set_default(self):
        instance = Instance(
            test_fixtures.name1,
            test_fixtures.region1,
            test_fixtures.project1,
            test_fixtures.connection_name1,
            False,
        )
        instance.set_default(True)
        assert instance.default is True


class TestSite:
    def test_setup_nicknames(self):
        site = Site(
            {
                test_fixtures.name1: test_fixtures.instance1,
                test_fixtures.name2: test_fixtures.instance2,
            }
        )
        site.set_up_nicknames()
        assert site.nicknames["database-postgres"] == [
            test_fixtures.instance1,
            test_fixtures.instance2,
        ]

    def test_update(self):
        site = Site(
            {
                test_fixtures.name1: test_fixtures.instance1,
                test_fixtures.name2: test_fixtures.instance2,
            }
        )
        name3 = "db-pg-instance-3"
        instance = Instance(
            name3,
            test_fixtures.region1,
            test_fixtures.project1,
            f"{test_fixtures.project1}:{test_fixtures.region1}:{name3}",
            False,
        )
        site.update(instance)
        assert instance.port == 5513

    def test_print_list(self):
        site = Site(
            {
                test_fixtures.name1: test_fixtures.instance1,
                test_fixtures.name2: test_fixtures.instance2,
            }
        )
        values = site.print_list(test_fixtures.project1)
        assert len(values) == 1
        assert (
            values[0]
            == "Project: project-1, Nick: database-postgres, Port 5511, Name: database-postgres-instance-1234, Region: region-1, IAM Enabled: False, Default: False"
        )

    def test_get_instance_by_nickname(self):
        site = Site(
            {
                test_fixtures.name1: test_fixtures.instance1,
                test_fixtures.name2: test_fixtures.instance2,
            }
        )
        site.set_up_nicknames()
        with raises(InstanceNotFoundError):
            site.get_instance_by_nick_name("fish", None)

        with_nick = site.get_instance_by_nick_name(
            "database-postgres", test_fixtures.project1
        )
        assert with_nick == test_fixtures.instance1

        name3 = "db-pg-instance-3"
        instance = Instance(
            name3,
            test_fixtures.region1,
            test_fixtures.project1,
            f"{test_fixtures.project1}:{test_fixtures.region1}:{name3}",
            False,
        )
        site.update(instance)
        site.set_up_nicknames()
        with raises(InstanceNotFoundError):
            site.get_instance_by_nick_name(instance.nick_name, test_fixtures.project2)

        with raises(DuplicateInstanceError):
            site.get_instance_by_nick_name("database-postgres", None)

    def test_get_default_instances(self):
        site = Site(
            {
                test_fixtures.name1: test_fixtures.instance1,
                test_fixtures.name2: test_fixtures.instance2,
            }
        )
        assert site.get_default_instances(None) == [test_fixtures.instance2]
        assert site.get_default_instances("project-1") == []
        assert site.get_default_instances("project-2") == [test_fixtures.instance2]

    def test_connection_names(self):
        assert test_fixtures.site1.connection_names() == [
            test_fixtures.connection_name1,
            test_fixtures.connection_name2,
        ]

    def test_add_instance(self):
        site = Site(
            {
                test_fixtures.name1: test_fixtures.instance1,
                test_fixtures.name2: test_fixtures.instance2,
            }
        )
        site.set_up_nicknames()
        name3 = "db-pg-instance-3"
        with raises(DuplicateInstanceError):
            site.add_instance(
                f"{test_fixtures.project1}:{test_fixtures.region1}:{name3}",
                "database-postgres",
                False,
            )
        with raises(DuplicateInstanceError):
            site.add_instance(
                f"{test_fixtures.project1}:{test_fixtures.region1}:{test_fixtures.name1}",
                "test-nick",
                False,
            )
        with raises(InvalidConnectionName):
            site.add_instance(f"{test_fixtures.project1}:{name3}", "test-nick", False)
        actual = site.add_instance(
            f"{test_fixtures.project1}:{test_fixtures.region1}:{name3}",
            "test-nick",
            False,
        )
        by_nick = site.get_instance_by_nick_name("test-nick", None)
        assert actual.name == name3
        assert actual.project == test_fixtures.project1
        assert by_nick == actual

    def test_remove_instances(self):
        site = Site(
            {
                test_fixtures.connection_name1: test_fixtures.instance1,
                test_fixtures.connection_name2: test_fixtures.instance2,
            }
        )
        site.set_up_nicknames()
        site.remove_instance(
            test_fixtures.instance1.connection_name,
        )
        with raises(InstanceNotFoundError):
            site.get_instance_by_nick_name(
                test_fixtures.instance1.nick_name, test_fixtures.instance1.project
            )
        assert test_fixtures.instance1.connection_name not in site.instances
