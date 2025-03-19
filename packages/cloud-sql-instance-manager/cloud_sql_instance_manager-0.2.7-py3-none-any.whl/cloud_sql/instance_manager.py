import sys
from typing import Dict, Optional
from cloud_sql.gcp import obtain_instances
from cloud_sql.cloud_sql_proxy import (
    run_cloud_sql_proxy,
    stop_cloud_sql_proxy,
    check_if_proxy_is_running,
)
from cloud_sql.commandline import get_parameters
from cloud_sql.config import Configuration, PathNotFoundError
from cloud_sql.instances import (
    Site,
    InstanceNotFoundError,
    DuplicateInstanceError,
    Instance,
    InvalidConnectionName,
)
from cloud_sql.persistence import Persistence, default_base_path
from cloud_sql.running_instances import RunningInstances


def refresh_running(running_instances: RunningInstances):
    running = running_instances.get_all_running()
    old_running = list(running.items())
    for (connection_name, pid) in old_running:
        if not check_if_proxy_is_running(pid, connection_name):
            running_instances.remove_running(connection_name)


def get_instance_from_nick(
    site: Site, nick: str, project: Optional[str]
) -> Optional[Instance]:
    try:
        return site.get_instance_by_nick_name(nick, project)
    except InstanceNotFoundError:
        print("No instance with that name or nick found.")
        return None
    except DuplicateInstanceError:
        print(
            "More than one instance with that name or nick found, try specifying a project with --project."
        )
        return None


def print_list(site: Site, project: Optional[str]):
    lines = site.print_list(project)
    for line in lines:
        print(line)


def print_list_running(site: Site, running_instances: RunningInstances):
    running = running_instances.get_all_running()
    for connection_name in running.keys():
        instance = site.instances[connection_name]
        print(instance.print(running[connection_name]))
    if len(running) == 0:
        print("No running instances")


def start(
    config: Configuration,
    site: Site,
    running_instances: RunningInstances,
    name: str,
    project: Optional[str],
):
    if name == "default":
        instances = site.get_default_instances(project)
        if len(instances) == 0:
            print("No default instances found")
    else:
        instances = [get_instance_from_nick(site, name, project)]
    for instance in instances:
        if running_instances.get_running(instance.connection_name):
            print(f"{instance.nick_name} is already running.")
        else:
            pid = run_cloud_sql_proxy(
                config.cloud_sql_path,
                instance.connection_name,
                instance.port,
                instance.iam,
            )
            running_instances.add_running(pid, instance.connection_name)
            print(f"Started {instance.name} on port {instance.port}")


def stop(
    site: Site,
    running_instances: RunningInstances,
    nickname: str,
    project: Optional[str],
):
    if nickname == "all":
        instances = [
            site.instances[name]
            for name in running_instances.get_all_running().keys()
            if (not project or project == site.instances[name].project)
        ]
        if len(instances) == 0:
            print("No running instances found")
    else:
        instances = [get_instance_from_nick(site, nickname, project)]

    for instance in instances:
        pid = running_instances.get_running(instance.connection_name)
        if pid:
            if stop_cloud_sql_proxy(pid, instance.connection_name):
                print(f"Stopped {instance.name} on port {instance.port}")
            else:
                print(
                    f"Could not locate process to stop for {instance.nick_name}, it has been removed from the running list"
                )
            running_instances.remove_running(instance.connection_name)
        else:
            print(f"{instance.nick_name} is not running")


def import_instances(config: Configuration, site: Site, project: Optional[str], tidy: Optional[bool]):

    (insert_count, delete_count) = obtain_instances(config, site, project, tidy)
    print(f"Imported {insert_count} instances.")
    if tidy:
        print(f"Removed {delete_count} instances.")
        
            

def update(
    site: Site,
    name: str,
    project: Optional[str],
    new_iam: Optional[str],
    new_nick: Optional[str],
    new_default: Optional[str],
):
    instance = get_instance_from_nick(site, name, project)
    if instance:

        if new_iam:
            instance.set_iam(new_iam.lower() == "true")

        if new_nick:
            try:
                other_instance = site.get_instance_by_nick_name(
                    new_nick, instance.project
                )
            except (InstanceNotFoundError, DuplicateInstanceError):
                other_instance = None
            if other_instance:
                print("That nick would not be unique, pick another.")
            else:
                instance.nick_name = new_nick
                site.set_up_nicknames()

        if new_default:
            instance.set_default(new_default.lower() == "true")

        print("Instance updated:")
        print(instance.print(None))


def update_config(
    config: Configuration, new_path: Optional[str], new_enable_iam: Optional[str]
):
    if new_path:
        try:
            config.new_path(new_path)
            print(f"Updated cloud_sql_proxy path to {new_path}")
        except PathNotFoundError:
            print(
                "That file appears not to exist. It needs to be the fully qualified path."
            )

    if new_enable_iam:
        config.set_enable_iam_by_default(new_enable_iam.lower() == "true")
        print(f"Updated default IAM setting to: {config.enable_iam_by_default}")

    if not new_enable_iam and not new_path:
        print(config.print())


def add_instance(
    config: Configuration, site: Site, connection_name: str, nick_name: Optional[str]
):
    try:
        new_instance = site.add_instance(
            connection_name, nick_name, config.enable_iam_by_default
        )
        print("Added new instance")
        print(new_instance.print(None))
    except (InvalidConnectionName, DuplicateInstanceError) as err:
        print(str(err))


def remove_instance(
    site: Site, running_instances: RunningInstances, name: str, project: Optional[str]
):
    instance = get_instance_from_nick(site, name, project)
    if instance:
        if instance.connection_name in running_instances.instances:
            stop(site, instance.nick_name, instance.project)
        site.remove_instance(instance.connection_name)
        print(f"Removed connection: {instance.connection_name}")


def execute_command(
    parameters: Dict[str, str],
    config: Configuration,
    site: Site,
    running_instances: RunningInstances,
):
    command = parameters["command"]

    if command == "list":
        print_list(site, parameters["project"])

    elif command == "list-running":
        print_list_running(site, running_instances)

    elif command == "start":
        start(
            config, site, running_instances, parameters["name"], parameters["project"]
        )

    elif command == "stop":
        stop(site, running_instances, parameters["name"], parameters["project"])

    elif command == "update":
        update(
            site,
            parameters["name"],
            parameters["project"],
            parameters["iam"],
            parameters["nick"],
            parameters["default"],
        )

    elif command == "import":
        import_instances(config, site, parameters["project"], parameters["tidy"])

    elif command == "config":
        update_config(config, parameters["path"], parameters["iam_default"])

    elif command == "add":
        add_instance(config, site, parameters["connection_name"], parameters["nick"])

    elif command == "remove":
        remove_instance(
            site, running_instances, parameters["name"], parameters["project"]
        )

    else:
        print("Specify a command or ask for help with --help")


def run():  # pragma: no cover
    persistence = Persistence(default_base_path())
    app_config = persistence.load_config()
    app_parameters = get_parameters(sys.argv[1:])
    site_info = persistence.load_site()
    running = persistence.load_running()
    refresh_running(running)
    execute_command(app_parameters, app_config, site_info, running)
    persistence.save_running(running)
    persistence.save_site(site_info)
    persistence.save_config(app_config)
    sys.exit()
