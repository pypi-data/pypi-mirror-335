from typing import List, Optional, Tuple

import google
from googleapiclient import discovery

from cloud_sql.config import Configuration
from cloud_sql.instances import Instance, Site


def get_credentials_and_project():
    a = google.auth.default()
    return a


def get_google_service(credentials):
    return discovery.build("sqladmin", "v1beta4")


def obtain_instances(
    config: Configuration, site: Site, override_project: Optional[str], tidy: Optional[bool]
) -> Tuple[int,int]:
    credentials, project = get_credentials_and_project()
    service = get_google_service(credentials)
    if override_project:
        project = override_project
    req = service.instances().list(project=project)
    resp = req.execute()
    instances = [
        Instance(
            item.get("name"),
            item.get("region"),
            item.get("project"),
            item.get("connectionName"),
            config.enable_iam_by_default,
        )
        for item in resp.get("items")
        if item.get("instanceType") == "CLOUD_SQL_INSTANCE"
    ]
    insert_count = 0
    delete_count = 0
    for instance in instances:
        if site.update(instance):
            insert_count += 1
    if tidy:
        project_instances : List[Instance] = [instance for instance in site.instances.values() if instance.project == project]
        connection_names = [instance.connection_name for instance in instances]
        for project_instance in project_instances:
            if project_instance.connection_name not in connection_names:
                site.remove_instance(project_instance.connection_name)
                delete_count += 1

    site.set_up_nicknames()
    return (insert_count, delete_count)