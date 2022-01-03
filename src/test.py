from mongoengine import *
from mongo_schema import *
import bottle_config
import db_api, utils
main_config = bottle_config.load()

connect(host="mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}?authSource=admin".format(**main_config))

# server1 = Server(cluster_name='lab', gr_name='C55153C1-1574-4972-BF06-7332D6AD46A7', server_id=1, server_name='mysql_01')
# server1.save()
# server2 = Server(cluster_name='lab', gr_name='C55153C1-1574-4972-BF06-7332D6AD46A7', server_id=2, server_name='mysql_02')
# server2.save()

# server3 = Server(cluster_name='lab2', gr_name='C55153C1-1574-4972-BF06-7332D6AD46A8', server_id=1, server_name='mysql_01')
# server3.save()
# server4 = Server(cluster_name='lab2', gr_name='C55153C1-1574-4972-BF06-7332D6AD46A8', server_id=2, server_name='mysql_02')
# server4.save()

# for server in Server.objects:
#     print(server.server_name)

# if Server.objects(cluster_name='lab', server_name='mysql_01'):
#     print('true')
# print(n_servers)

# data = {'gr_name': 'C55153C1-1574-4972-BF06-7332D6AD46A7'}
# result = db_api.get_cluster_members(data)
# print(result)

# data = {'gr_name': 'C55153C1-1574-4972-BF06-7332D6AD46A7', 'server_name': 'test2'}
# cluster_result = db_api.get_server_id(data)
# print(cluster_result)

# result = db_api.get_last_id(data=data)
# print(result)

# set_id = db_api.increment_last_id(data=data)
# print(set_id)

# reachable = utils.is_server_reachable('googhhhghle.com')
# print(reachable)

#cluster = Cluster(gr_name='C55153C1-1574-4972-BF06-7332D6AD46A7').save()
cluster = Cluster.objects(gr_name='C55153C1-1574-4972-BF06-7332D6AD46A7').first()
# server1 = Server(server_id=1, server_name='mysql_01', cluster=cluster)
# server1.save()
# server2 = Server(server_id=2, server_name='mysql_02', cluster=cluster)
# server2.save()

# cluster.servers = [server1.server_name, server2.server_name]
# cluster.save()

# cluster = Cluster.objects(gr_name='C55153C1-1574-4972-BF06-7332D6AD46A7').first()
# print(cluster.cluster_name)
# for server in cluster.servers:
#     print(server)

# server3 = Server(server_id=3, server_name='mysql_03', cluster=cluster)
# server3.save()

# cluster.servers.append(server3.server_name)
# cluster.save()

# servers = Server.objects()
# for server in servers:
#     print(server.server_name)

# cluster_id = ClusterId(
#         last_id=0,
#         cluster=cluster,
#     )
# cluster_id.save()
cluster_id = ClusterId.objects(cluster=cluster).first()
print(cluster_id.cluster.gr_name)

servers = Server.objects(cluster=cluster, server_name='mysql_03')
for server in servers:
    print(server.server_name)