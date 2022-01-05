from mongo_schema import Cluster,Server,ClusterId
import utils, security_lib
import uuid, json, secrets, base64

PASSWORD_LEN = 20

def encodepw(password):
    encoded_pw = base64.b64encode(password.encode("utf-8")).decode('utf8')
    return encoded_pw

def init_cluster(data):
    errors = []
    result = {}
    try:
        cluster = Cluster.objects(cluster_name=data['cluster_name']).first()
        if not cluster:

            operator_user = data.get('operator_user')
            if not operator_user:
                operator_user = 'operator'
                
            operator_pw = data.get('operator_pw')
            if not operator_pw:
                operator_pw = secrets.token_urlsafe(PASSWORD_LEN)
            operator_pw_hash = security_lib.encode(operator_pw)
            
            replica_user = data.get('replica_user')
            if not replica_user:
                replica_user = 'replica'
            
            replica_pw = data.get('replica_pw')
            if not replica_pw:
                replica_pw = secrets.token_urlsafe(PASSWORD_LEN)
            replica_pw_hash = security_lib.encode(replica_pw)

            cluster = Cluster(
                cluster_name=data['cluster_name'],
                gr_name=str(uuid.uuid4()),
                gr_vcu=str(uuid.uuid4()),
                operator_user=operator_user,
                operator_pw=operator_pw_hash.decode('utf-8'),
                replica_user=replica_user,
                replica_pw=replica_pw_hash.decode('utf-8'),
            )
            cluster.save()

            cluster_id = ClusterId(
                last_id=0,
                cluster=cluster,
            )
            cluster_id.save()
        else:
            operator_pw = security_lib.decode(cluster.operator_pw.encode('utf8'))
            replica_pw = security_lib.decode(cluster.replica_pw.encode('utf8'))

        result['exit_code'] = 1
        result['gr_name'] = cluster.gr_name
        result['gr_vcu'] = cluster.gr_vcu
        result['operator_user'] = cluster.operator_user
        result['operator_pw'] = encodepw(operator_pw)
        result['replica_user'] = cluster.replica_user
        result['replica_pw'] =  encodepw(replica_pw)
    except Exception as e:
        result['exit_code'] = 0
        errors.append(e)
    return {'errors': errors, 'data': result}

def increment_last_id(data, size=1):
    errors = []
    try:
        cluster = Cluster.objects(cluster_name=data['cluster_name']).first()
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
        cluster = Cluster.objects(cluster_name=data['cluster_name']).first()
        cluster_id = ClusterId.objects(cluster=cluster).first()
        last_id = last_id_obj.last_id
    except Exception as e:
        errors.append(e)
        last_id = None
    return {'errors': errors, 'data': last_id}

def get_clusters(output='dict'):
    errors = []
    clusters = Cluster.objects()
    if output == 'dict':
        clusters_json = clusters.to_json()
        clusters_dict = json.loads(clusters_json)
        return {'errors': errors, 'data': clusters_dict}
    elif output == 'web':
        return {'errors': errors, 'data': clusters}

def get_servers(cluster_name=None, output='dict'):
    errors = []
    if cluster_name:
        cluster = Cluster.objects(cluster_name=cluster_name).first()
        servers = Server.objects(cluster=cluster)
    else:
        servers = Server.objects()
    
    if output == 'dict':
        servers_json = servers.to_json()
        servers_dict = json.loads(servers_json)
        return {'errors': errors, 'data': servers_dict}
    elif output == 'web':
        return {'errors': errors, 'data': servers}

def get_cluster_members(data):
    errors = []
    result = {'members': []}
    try:
        available_servers = 0
        cluster = Cluster.objects(cluster_name=data['cluster_name']).first()
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
        cluster = Cluster.objects(cluster_name=data['cluster_name']).first()
        server_obj = Server.objects(cluster=cluster, server_name=data['server_name']).first()

        if server_obj:
            server_exist = True
            result['server_id'] = server_obj.server_id
        else:
            server_id_result = increment_last_id(data=data)
            server_id = server_id_result['data']
            root_pw = security_lib.encode(data['my_root_pw'])
            
            new_server = Server(
                cluster=cluster,
                server_id=server_id, 
                server_name=data['server_name'],
                root_pw=root_pw.decode('utf-8'),
            )
            new_server.save()
            result['server_id'] = server_id
    except Exception as e:
        errors.append(e)
        n_servers = 0
        server_id = None
    return {'errors': errors, 'data': result}