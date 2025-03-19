import subprocess
from typing import Optional

import psutil as psutil
from psutil import NoSuchProcess


class CloudProxyNotFoundError(Exception):
    pass


def run_cloud_sql_proxy(
    cloud_sql_proxy_path: str, connection_name: str, port: int, enable_iam: bool
) -> int:
    instance_description = "-instances={}=tcp:{}".format(connection_name, port)

    if cloud_sql_proxy_path is None:
        raise CloudProxyNotFoundError("Could not find cloud_sql_proxy path")

    if enable_iam:
        command = [cloud_sql_proxy_path, "-enable_iam_login", instance_description]
    else:
        command = [cloud_sql_proxy_path, instance_description]

    process = subprocess.Popen(command, start_new_session=True)

    return process.pid


def stop_cloud_sql_proxy(pid: int, name: str) -> bool:
    process = check_if_proxy_is_running(pid, name)
    if process:
        process.kill()
        return True
    else:
        return False


def check_if_proxy_is_running(pid: int, name: str) -> Optional[psutil.Process]:
    try:
        process = psutil.Process(pid)
    except NoSuchProcess:
        process = None
    if process:
        cmdline = process.cmdline()
        if name in str(cmdline):
            return process
    return None
