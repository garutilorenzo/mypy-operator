import json, pprint, time, datetime, os
import urllib.request
import urllib.parse
from mysqlsh import mysql
import security_lib

OPERATOR_URL = os.getenv('OPERATOR_URL')
OPERATOR_SECRET = os.getenv('OPERATOR_SECRET')
ORC_TOPOLOGY_USER = os.getenv('ORC_TOPOLOGY_USER')
ORC_TOPOLOGY_PASSWORD = os.getenv('ORC_TOPOLOGY_PASSWORD')
UPDATE_TIME_ENV = os.getenv('UPDATE_TIME')
UPDATE_TIME = 30 if not UPDATE_TIME_ENV else UPDATE_TIME_ENV

def get_servers(cluster_name):
    servers_result = []
    server_url = '{}/api/get/servers'.format(OPERATOR_URL)
    server_args = {'auth_key': OPERATOR_SECRET, 'cluster_name': cluster_name}
    server_params = json.dumps(server_args).encode('utf8')

    try:
        server_req = urllib.request.Request(server_url, data=server_params,
            headers={'content-type': 'application/json'})
        server_response = urllib.request.urlopen(server_req)
        server_json = json.loads(server_response.read().decode('utf8'))
        if not server_json.get('errors'):
            servers = server_json['data']
            for server in servers:
                servers_result.append(server)
    except Exception as e:
        print(f'Error reading from operator web api')

    return servers_result

def update_cluster_status(cluster_name, cluster_status):
    server_url = '{}/api/update/cluster'.format(OPERATOR_URL)
    server_args = {'auth_key': OPERATOR_SECRET, 'cluster_name': cluster_name, 'cluster_status': cluster_status}
    server_params = json.dumps(server_args).encode('utf8')

    try:
        server_req = urllib.request.Request(server_url, data=server_params,
            headers={'content-type': 'application/json'})
        server_response = urllib.request.urlopen(server_req)
        server_json = json.loads(server_response.read().decode('utf8'))
        exit_code = 0
        if not server_json.get('errors'):
            exit_code = server_json['data']['exit_code']
    except Exception as e:
        print(f'Error reading from operator web api')
        exit_code = 1
    return exit_code

def get_time_from_creation(created_time):
    c_time = datetime.datetime.fromtimestamp(created_time/1000)
    now  = datetime.datetime.now()
    duration = now - c_time
    duration_in_s = duration.total_seconds()
    return duration_in_s

def cluster_exist(cluster_name):
    try:
        cluster = dba.get_cluster(cluster_name)
        is_cluster_exist = True
    except Exception as e:
        is_cluster_exist = False
    return is_cluster_exist

def mysql_session(server, root_pw, schema=''):
    root_pw_parsed = urllib.parse.quote(root_pw)
    conn_string = 'root:{}@{}'.format(root_pw_parsed, server)
    if schema:
        conn_string = 'root:{}@{}/{}'.format(root_pw_parsed, server, schema)
    try:
        mySession = mysql.get_classic_session(conn_string)
    except Exception as e:
        mySession = None
    return mySession

def shell_session_open(server, user, user_pw):
    user_pw_parsed = urllib.parse.quote(user_pw)
    try:
        shSession = shell.connect('mysql://{}:{}@{}'.format(user, user_pw_parsed, server))
    except Exception as e:
        shSession = None
    return shSession

def shell_session_close():
    try:
        shSession = shell.disconnect()
    except Exception as e:
        shSession = None
    return shSession

def get_primary(first_server, root_pw):
    conn = mysql_session(first_server, root_pw)
    if conn:
        get_primary_sql = '''
            select CONCAT(member_host, ':', member_port) as primary_host 
            from performance_schema.replication_group_members where member_state='ONLINE' 
            and member_id=(
                IF
                (
                    (select @grpm:=variable_value from performance_schema.global_status where variable_name='group_replication_primary_member') = '', member_id, @grpm
                )
            ) 
            limit 1
        '''
        get_primary_result = conn.run_sql(get_primary_sql).fetch_one()
        conn.close()
        return get_primary_result[0]
    return None

def create_orchestrator_user(primary_server, root_pw):
    conn = mysql_session(primary_server, root_pw, 'mysql')
    if conn:
        user_exists_sql = "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '{}')".format(ORC_TOPOLOGY_USER)
        user_exists = conn.run_sql(user_exists_sql).fetch_one()
        if int(user_exists[0]) == 0:
            create_user_sql_list = [
            "CREATE USER IF NOT EXISTS '{}'@'%' IDENTIFIED BY '{}';".format(ORC_TOPOLOGY_USER, ORC_TOPOLOGY_PASSWORD),
            "GRANT SUPER, PROCESS, REPLICATION SLAVE, REPLICATION CLIENT, RELOAD ON *.* TO '{}'@'%';".format(ORC_TOPOLOGY_USER),
            "GRANT SELECT ON mysql.slave_master_info TO '{}'@'%';".format(ORC_TOPOLOGY_USER),
            "GRANT SELECT ON meta.* TO '{}'@'%';".format(ORC_TOPOLOGY_USER),
            "GRANT SELECT ON performance_schema.replication_group_members TO '{}'@'%';".format(ORC_TOPOLOGY_USER),
            ]
            for statement in create_user_sql_list:
                statement_result = conn.run_sql(statement)
        conn.close()

def create_cluster(cluster_name):
    try:
        create_cluster_result = dba.create_cluster(cluster_name, {'adoptFromGR': True})
    except Exception as e:
        create_cluster_result = None
    return create_cluster_result

def add_server(cluster, cluster_status):
    cluster_servers = cluster_status['defaultReplicaSet']['topology'].keys()
         
    for server in cluster_servers:
        add_instance = False
        if cluster_status['defaultReplicaSet']['topology'][server].get('instanceErrors', None):
            for error in cluster_status['defaultReplicaSet']['topology'][server]['instanceErrors']:
                if 'Instance is not managed by InnoDB cluster' in error:
                    add_instance = True
        if add_instance:
            cluster.add_instance(server)

def operator_run():
    cluster_url = '{}/api/get/clusters'.format(OPERATOR_URL)
    cluster_args = {'auth_key': OPERATOR_SECRET}
    cluster_params = json.dumps(cluster_args).encode('utf8')

    while True:
        try:
            cluster_req = urllib.request.Request(cluster_url, data=cluster_params,
                    headers={'content-type': 'application/json'})
            cluster_response = urllib.request.urlopen(cluster_req)
            cluster_json = json.loads(cluster_response.read().decode('utf8'))
            if not cluster_json.get('errors'):
                clusters = cluster_json['data']
                for cluster in clusters:

                    operator_user = cluster['operator_user']
                    operator_pw_enc = cluster['operator_pw']
                    operator_pw = security_lib.decode(operator_pw_enc.encode('utf8'))

                    servers = get_servers(cluster_name=cluster['cluster_name'])
                    if servers:
                        first_server = servers[0]['server_name']
                        root_pw_enc = servers[0]['root_pw']
                        root_pw = security_lib.decode(root_pw_enc.encode('utf8'))

                        seconds_from_creation = get_time_from_creation(cluster['created_time']['$date'])
                        if seconds_from_creation <= 120:
                            update_cluster_status(cluster['cluster_name'], 'init')
                            print('Cluster name: {} discovered, waiting 120 seconds before init'.format(cluster['cluster_name']))
                            continue

                        primary_server = get_primary(first_server, root_pw)
                        primary_server_data = [s for s in servers if s['server_name'] in primary_server][0]
                        primary_server_pw_enc = primary_server_data['root_pw']
                        primary_server_pw = security_lib.decode(primary_server_pw_enc.encode('utf8'))
                        create_orchestrator_user(primary_server, primary_server_pw)

                        if not primary_server:
                            continue

                        if shell_session_open(primary_server, operator_user, operator_pw):
                            is_cluster_exist = cluster_exist(cluster['cluster_name'])
                            if not is_cluster_exist:
                                res = create_cluster(cluster_name=cluster['cluster_name'])
                                update_cluster_status(cluster['cluster_name'], 'online')
                            else:
                                cluster = dba.get_cluster(cluster['cluster_name'])
                                cluster_status = cluster.status()
                                print(cluster_status)

                                add_server(cluster, cluster_status)

                            shell_session_close()
            
            print('Sleep for {}'.format(str(UPDATE_TIME)))
            time.sleep(UPDATE_TIME)
            
        except StopIteration:
            print(f'Error reading from operator web api')

if __name__ == '__main__':
    operator_run()