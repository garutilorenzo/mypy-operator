import json, pprint
from mysqlsh import mysql
session = shell.connect('mysql://root:root@mysql_node01:3306')

def get_cluster():
    res = dba.get_cluster()
    return res

def get_cluster_status(cluster):
    cluster_status = cluster.status()
    print(cluster_status)
    return cluster_status

if __name__ == '__main__':
    cluster = get_cluster()
    get_cluster_status(cluster)