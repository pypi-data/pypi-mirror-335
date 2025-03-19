import os
import shutil


class PathNotFoundError(Exception):
    pass


class Configuration(object):
    def __init__(self, cloud_sql_path, enable_iam_by_default):
        self.cloud_sql_path = cloud_sql_path
        self.enable_iam_by_default = enable_iam_by_default

    def new_path(self, new_path):
        if os.path.exists(new_path):
            self.cloud_sql_path = new_path
        else:
            raise PathNotFoundError

    def set_enable_iam_by_default(self, new_enable_iam_by_default):
        self.enable_iam_by_default = new_enable_iam_by_default

    def check(self):  # pragma: no cover
        if not hasattr(self, "enable_iam_by_default"):
            self.enable_iam_by_default = True

    def print(self) -> str:
        return f"Cloud SQL Proxy path: {self.cloud_sql_path} Enable IAM by Default: {self.enable_iam_by_default}"


def default_configuration():
    return Configuration(shutil.which("cloud_sql_proxy"), True)
