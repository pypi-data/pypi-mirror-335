import json
from typing import Dict, Optional, List

import jsonpickle


class InstanceNotFoundError(Exception):
    pass


class DuplicateInstanceError(Exception):
    pass


class InvalidConnectionName(Exception):
    pass


class Instance(object):
    def __init__(
        self,
        name: str,
        region: str,
        project: str,
        connection_name: str,
        enable_iam: bool,
    ):
        self.port = None
        self.iam = enable_iam
        self.default = False
        self.name = name
        self.nick_name = name[: name.find("-instance-")]
        self.region = region
        self.project = project
        self.connection_name = connection_name

    def __repr__(self):  # pragma: no cover
        return json.dumps(self.__dict__)

    def assign_port(self, port: int):
        self.port = port

    def print(self, pid: Optional[int]) -> str:
        if not pid:
            return f'Project: {self.project}, Nick: {self.nick_name}, Port {self.port or "N/A"}, Name: {self.name}, Region: {self.region}, IAM Enabled: {self.iam}, Default: {self.default}'
        else:
            return f'Pid: {pid}, Project: {self.project}, Nick: {self.nick_name}, Port {self.port or "N/A"}, Name: {self.name}, Region: {self.region}, IAM Enabled: {self.iam}, Default: {self.default}'

    def set_iam(self, iam: bool):
        self.iam = iam

    def set_default(self, default: bool):
        self.default = default

    def check(self):  # pragma: no cover
        if not hasattr(self, "default"):
            self.default = False
        if hasattr(self, "shortname") and not hasattr(self, "nick_name"):
            self.nick_name = self.shortname
            delattr(self, "shortname")


class Site(object):
    def __init__(self, instances: Dict[str, Instance]):
        self.nicknames = {}
        self.instances = instances
        self.nextPort = 0
        ports = [
            instance.port
            for instance in instances.values()
            if instance.port is not None
        ]
        ports.insert(0, 5433)
        self.nextPort = max(ports) + 1

    def __repr__(self):  # pragma: no cover
        return jsonpickle.encode(self)

    def connection_names(self) -> List[str]:
        return [instance.connection_name for instance in self.instances.values()]

    def set_up_nicknames(self):
        self.nicknames = {}
        for instance in self.instances.values():
            if instance.nick_name in self.nicknames.keys():
                if instance not in self.nicknames[instance.nick_name]:
                    self.nicknames[instance.nick_name].append(instance)
            else:
                self.nicknames[instance.nick_name] = [instance]

    def update(self, instance: Instance) -> bool:
        if instance.connection_name not in self.instances.keys():
            if instance.port is None:
                instance.port = self.nextPort
                self.nextPort += 1
            self.instances[instance.connection_name] = instance
            return True
        else:
            return False

    def print_list(self, project: Optional[str]) -> List[str]:
        return [
            instance.print(None)
            for instance in sorted(
                self.instances.values(),
                key=lambda instance: f"{instance.project}{instance.nick_name}",
            )
            if (not project) or (instance.project == project)
        ]

    def get_instance_by_nick_name(self, name, project) -> Optional[Instance]:

        if name not in self.nicknames:
            raise InstanceNotFoundError("No instance found with that nickname")

        possibles = self.nicknames[name]

        if project:
            possibles = [
                possible for possible in possibles if possible.project == project
            ]

        if not possibles:
            raise InstanceNotFoundError(
                "No instance found with that nickname for that project"
            )
        else:
            if len(possibles) == 1:
                return possibles[0]
            else:
                raise DuplicateInstanceError(
                    "More than one instance with that nick - specify a project, or change the nickname"
                )

    def get_default_instances(self, project) -> List[Instance]:
        return [
            instance
            for instance in self.instances.values()
            if (not project or instance.project == project) and instance.default
        ]

    def check(self):
        for instance in self.instances.values():
            instance.check()

    def add_instance(
        self, connection_name: str, nick_name: Optional[str], enable_iam: bool
    ) -> Instance:
        split_connection_name = connection_name.split(":")
        if len(split_connection_name) != 3:
            raise InvalidConnectionName(
                "Connection name should be in the format name:region:connectionName"
            )

        project = split_connection_name[0]
        name = split_connection_name[2]

        instance = Instance(
            name,
            split_connection_name[1],
            project,
            connection_name,
            enable_iam,
        )

        if nick_name:
            try:
                self.get_instance_by_nick_name(nick_name, project)
            except:
                instance.nick_name = nick_name
            else:
                raise DuplicateInstanceError(
                    "An instance already exists for that nick_name and project"
                )

        if connection_name in self.connection_names():
            raise DuplicateInstanceError(
                "An instance already exists for that name and project"
            )

        self.update(instance)
        self.set_up_nicknames()
        return instance

    def remove_instance(self, connection_name: str):
        self.instances.pop(connection_name)
        self.set_up_nicknames()
