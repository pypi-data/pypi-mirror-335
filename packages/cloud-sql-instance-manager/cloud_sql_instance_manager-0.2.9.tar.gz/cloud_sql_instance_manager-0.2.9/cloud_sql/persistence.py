import os
import os.path

import jsonpickle

from cloud_sql.config import Configuration, default_configuration
from cloud_sql.instances import Site
from cloud_sql.running_instances import RunningInstances


def default_base_path() -> str:
    return os.path.join(os.getenv("HOME"), ".cloudsql")


class Persistence(object):
    def __init__(self, base_path: str):
        self.instance_filename = os.path.join(base_path, "instances.json")
        self.config_filename = os.path.join(base_path, "config.json")
        self.running_instances_filename = os.path.join(base_path, "running.json")

    def save_site(self, site: Site):
        if not os.path.exists(os.path.dirname(self.instance_filename)):
            os.makedirs(os.path.dirname(self.instance_filename))

        with open(self.instance_filename, "w") as f:
            f.write(jsonpickle.encode(site))

    def load_site(self) -> Site:
        if not os.path.exists(self.instance_filename):
            return Site({})
        else:
            with open(self.instance_filename, "r") as f:
                json_str = f.read()
                site = jsonpickle.decode(json_str)
                site.check()
                return site

    def save_config(self, config: Configuration):
        if not os.path.exists(os.path.dirname(self.config_filename)):
            os.makedirs(os.path.dirname(self.config_filename))

        with open(self.config_filename, "w") as f:
            f.write(jsonpickle.encode(config))

    def load_config(self) -> Configuration:
        if not os.path.exists(self.config_filename):
            return default_configuration()
        else:
            with open(self.config_filename, "r") as f:
                json_str = f.read()
                config = jsonpickle.decode(json_str)
                config.check()
                return config

    def save_running(self, running_instances: RunningInstances):
        if not os.path.exists(os.path.dirname(self.running_instances_filename)):
            os.makedirs(os.path.dirname(self.running_instances_filename))

        with open(self.running_instances_filename, "w") as f:
            f.write(jsonpickle.encode(running_instances))

    def load_running(self) -> RunningInstances:
        if not os.path.exists(self.running_instances_filename):
            return RunningInstances({})
        else:
            with open(self.running_instances_filename, "r") as f:
                json_str = f.read()
                return jsonpickle.decode(json_str)
