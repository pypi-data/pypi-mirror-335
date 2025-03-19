from cloud_sql.config import Configuration
from cloud_sql.instances import Instance, Site
from cloud_sql.running_instances import RunningInstances

name1 = "database-postgres-instance-1234"
project1 = "project-1"
region1 = "region-1"
port1 = 5511
connection_name1 = f"{project1}:{region1}:{name1}"
instance1 = Instance(name1, region1, project1, connection_name1, False)
instance1.port = port1
name2 = "database-postgres-instance-1235"
project2 = "project-2"
region2 = "region-2"

connection_name2 = f"{project2}:{region2}:{name2}"
port2 = 5512
instance2 = Instance(name2, region2, project2, f"{project2}:{region2}:{name2}", False)
instance2.port = port2
instance2.set_default(True)

name3 = "database-postgres-instance-1236"
connection_name3 = f"{project1}:{region1}:{name3}"
port3 = 5534
instance3 = Instance(name3, region1, project1, connection_name3, False)
instance3.port = port3
site1 = Site({connection_name1: instance1, connection_name2: instance2})

config1 = Configuration("path/to/cloud_sql", False)

pid1 = 1111
pid2 = 1112
running_instances1 = RunningInstances({name1: pid1, name2: pid2})
