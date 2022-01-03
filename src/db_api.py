from mongo_schema import Cluster,Server,ClusterId
import utils

def init_cluster(data):
    errors = []
    try:
        cluster = Cluster.objects(gr_name=data['gr_name']).first()
        if not cluster:
            cluster = Cluster(
                gr_name=data['gr_name'],
            )
            cluster.save()

            cluster_id = ClusterId(
                last_id=0,
                cluster=cluster,
            )
            cluster_id.save()
        result = 1
    except Exception as e:
        result = 0
        errors.append(e)
    return {'errors': errors, 'data': result}

def increment_last_id(data, size=1):
    errors = []
    try:
        cluster = Cluster.objects(gr_name=data['gr_name']).first()
        cluster_id = ClusterId.objects(cluster=cluster).first()
        new_id = cluster_id.last_id + size
        cluster_id.last_id = new_id
        cluster_id.save()
        last_id = new_id
    except Exception as e:
        errors.append(e)
    return {'errors': errors, 'data': last_id}

def get_last_id(data):
    errors = []
    try:
        cluster = Cluster.objects(gr_name=data['gr_name']).first()
        cluster_id = ClusterId.objects(cluster=cluster).first()
        last_id = last_id_obj.last_id
    except Exception as e:
        errors.append(e)
        last_id = None
    return {'errors': errors, 'data': last_id}

def get_clusters():
    clusters = Cluster.objects()
    return clusters

def get_servers(cluster=None):
    if cluster:
        servers = Server.objects(cluster=cluster)
    else:
        servers = Server.objects()
    return servers

def get_cluster_members(data):
    errors = []
    result = {'members': []}
    try:
        available_servers = 0
        cluster = Cluster.objects(gr_name=data['gr_name']).first()
        servers = Server.objects(cluster=cluster)
        for server in servers:
            if utils.is_server_reachable(server.server_name):
                available_servers +=1
            result['members'].append(server.server_name)
        result['available_servers'] = available_servers
    except Exception as e:
        errors.append(e)
        result['available_servers'] = None
    return {'errors': errors, 'data': result}

def get_server_id(data):
    errors = []
    result = {}
    try:
        server_exist = False
        cluster = Cluster.objects(gr_name=data['gr_name']).first()
        server_obj = Server.objects(cluster=cluster, server_name=data['server_name']).first()

        if server_obj:
            server_exist = True
            result['server_id'] = server_obj.server_id
        else:
            server_id_result = increment_last_id(data=data)
            server_id = server_id_result['data']
            
            new_server = Server(
                cluster=cluster,
                server_id=server_id, 
                server_name=data['server_name']
            )
            new_server.save()
            result['server_id'] = server_id
    except Exception as e:
        errors.append(e)
        n_servers = 0
        server_id = None
    return {'errors': errors, 'data': result}