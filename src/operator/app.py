import os, sys, json, urllib
from bottle import Bottle, run, \
     template, view, debug, static_file, request, response, redirect, TEMPLATE_PATH, SimpleTemplate
import bottle_config, db_api, utils
from mongoengine import *

main_config = bottle_config.load()

dirname = '/app/src/{}/'.format(os.getenv('BOTTLE_APP_NAME'))

TEMPLATE_PATH.insert(0, '{}/views/'.format(dirname))
# Main Bottle app/application
app = application = Bottle()

# Mongo
connect(host="mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}?authSource=admin".format(**main_config))

# Template default variables
SimpleTemplate.defaults["url"] = lambda: request.url
SimpleTemplate.defaults["fullpath"] = lambda: request.fullpath
SimpleTemplate.defaults["nav_pages"] = utils.build_nav_pages()
SimpleTemplate.defaults["nav_dropdown_pages"] = utils.build_nav_dropdown_pages()
SimpleTemplate.defaults["get_servers"] = db_api.get_servers
SimpleTemplate.defaults["is_server_reachable"] = utils.is_server_reachable

debug(main_config['enable_debug'])

@app.route('/static/<filename:re:.*\.css>')
def send_css(filename):
    response = static_file(filename, root=dirname+'/static/asset/css')
    response.set_header("Cache-Control", "public, max-age=604800")
    return response

@app.route('/static/<filename:re:.*\.js>')
def send_js(filename):
    response = static_file(filename, root=dirname+'/static/asset/js')
    response.set_header("Cache-Control", "public, max-age=604800")
    return response

@app.route('/static/<filename:re:.*\.map>')
def send_js(filename):
    response = static_file(filename, root=dirname+'/static/asset/map_files')
    response.set_header("Cache-Control", "public, max-age=604800")
    return response

@app.route('/static/img/<filename:path>')
def send_img(filename):
    response = static_file(filename, root=dirname+'/static/asset/img')
    response.set_header("Cache-Control", "public, max-age=604800") 
    return response

@app.error(404)
@view('index')
def error404(err):
    return dict(page_name='404', error_message='Nothing here, sorry')

@app.route('/')
@view('index')
def index():
    return dict(page_name='home')

@app.route('/clusters')
@view('clusters')
def clusters():
    clusters_result = db_api.get_clusters(output='web')
    clusters = clusters_result['data']
    return dict(page_name='clusters', clusters=clusters)

@app.route('/servers')
@view('servers')
def servers():
    servers_result = db_api.get_servers(output='web')
    servers = servers_result['data']
    return dict(page_name='servers', servers=servers)

### API-REST ###

@app.route('/api/get/init_cluster', method='POST')
def api_get_init_cluster():
    result = {'errors': [], 'data': []}
    params = ['cluster_name', 'operator_user', 'operator_pw', 'replica_user', 'replica_pw', 'auth_key']
   
    # parse input data
    try:
        data = request.json
    except ValueError:
        response.status = 400
        response.set_header("Content-Type", 'application/json')
        result['errors'].append('Value error, only application/json objects acepted')
        return json.dumps(result, indent=4, sort_keys=True)
    
    
    for key in data.keys():
        if key not in params:
            response.status = 400
            response.set_header("Content-Type", 'application/json')
            result['errors'].append('{} params not acepted'.format(key))
            return json.dumps(result, indent=4, sort_keys=True)
    
    for value in params:
        data[value] = data.get(value, '')
    
    if not data['auth_key'] or data['auth_key'] != 'CHANGE_ME':
        response.status = 401
        response.set_header("Content-Type", 'application/json')
        result['errors'].append('access denied')
        return json.dumps(result, indent=4, sort_keys=True)

    init_result = db_api.init_cluster(data)
    if init_result.get('errors'):
        response.status = 500
        response.set_header("Content-Type", 'application/json')
        result['errors'].extend(str(init_result['errors']))
        return json.dumps(result, indent=4, sort_keys=True)

    # return 200 Success
    response.set_header("Content-Type", 'application/json')
    return json.dumps(init_result, indent=4, sort_keys=True)

@app.route('/api/get/clusters', method='POST')
def api_get_clusters():
    result = {'errors': [], 'data': []}
    params = ['auth_key']
   
    # parse input data
    try:
        data = request.json
    except ValueError:
        response.status = 400
        response.set_header("Content-Type", 'application/json')
        result['errors'].append('Value error, only application/json objects acepted')
        return json.dumps(result, indent=4, sort_keys=True)
    
    
    for key in data.keys():
        if key not in params:
            response.status = 400
            response.set_header("Content-Type", 'application/json')
            result['errors'].append('{} params not acepted'.format(key))
            return json.dumps(result, indent=4, sort_keys=True)
    
    for value in params:
        data[value] = data.get(value, '')
    
    if not data['auth_key'] or data['auth_key'] != 'CHANGE_ME':
        response.status = 401
        response.set_header("Content-Type", 'application/json')
        result['errors'].append('access denied')
        return json.dumps(result, indent=4, sort_keys=True)

    clusters_result = db_api.get_clusters()
    if clusters_result.get('errors'):
        response.status = 500
        response.set_header("Content-Type", 'application/json')
        result['errors'].extend(str(clusters_result['errors']))
        return json.dumps(result, indent=4, sort_keys=True)

    # return 200 Success
    response.set_header("Content-Type", 'application/json')
    return json.dumps(clusters_result, indent=4, sort_keys=True)

@app.route('/api/get/servers', method='POST')
def api_get_servers():
    result = {'errors': [], 'data': []}
    params = ['cluster_name', 'auth_key']
   
    # parse input data
    try:
        data = request.json
    except ValueError:
        response.status = 400
        response.set_header("Content-Type", 'application/json')
        result['errors'].append('Value error, only application/json objects acepted')
        return json.dumps(result, indent=4, sort_keys=True)
    
    
    for key in data.keys():
        if key not in params:
            response.status = 400
            response.set_header("Content-Type", 'application/json')
            result['errors'].append('{} params not acepted'.format(key))
            return json.dumps(result, indent=4, sort_keys=True)
    
    for value in params:
        data[value] = data.get(value, '')
    
    if not data['auth_key'] or data['auth_key'] != 'CHANGE_ME':
        response.status = 401
        response.set_header("Content-Type", 'application/json')
        result['errors'].append('access denied')
        return json.dumps(result, indent=4, sort_keys=True)

    if data.get('cluster_name'):
        servers_result = db_api.get_servers(cluster_name=data['cluster_name'])
    else:
        servers_result = db_api.get_servers()

    if servers_result.get('errors'):
        response.status = 500
        response.set_header("Content-Type", 'application/json')
        result['errors'].extend(str(servers_result['errors']))
        return json.dumps(result, indent=4, sort_keys=True)

    # return 200 Success
    response.set_header("Content-Type", 'application/json')
    return json.dumps(servers_result, indent=4, sort_keys=True)

@app.route('/api/get/cluster_members', method='POST')
def api_get_cluster_members():
    result = {'errors': [], 'data': []}
    params = ['cluster_name', 'operator_user', 'operator_pw', 'replica_user', 'replica_pw', 'auth_key']
   
    # parse input data
    try:
        data = request.json
    except ValueError:
        response.status = 400
        response.set_header("Content-Type", 'application/json')
        result['errors'].append('Value error, only application/json objects acepted')
        return json.dumps(result, indent=4, sort_keys=True)
    
    
    for key in data.keys():
        if key not in params:
            response.status = 400
            response.set_header("Content-Type", 'application/json')
            result['errors'].append('{} params not acepted'.format(key))
            return json.dumps(result, indent=4, sort_keys=True)
    
    for value in params:
        data[value] = data.get(value, '')
    
    if not data['auth_key'] or data['auth_key'] != 'CHANGE_ME':
        response.status = 401
        response.set_header("Content-Type", 'application/json')
        result['errors'].append('access denied')
        return json.dumps(result, indent=4, sort_keys=True)

    cluster_result = db_api.get_cluster_members(data)
    if cluster_result.get('errors'):
        response.status = 500
        response.set_header("Content-Type", 'application/json')
        result['errors'].extend(''.join(str(cluster_result['errors'])))
        return json.dumps(result, indent=4, sort_keys=True)

    # return 200 Success
    response.set_header("Content-Type", 'application/json')
    return json.dumps(cluster_result, indent=4, sort_keys=True)

@app.route('/api/get/server_id', method='POST')
def api_get_server_id():
    result = {'errors': [], 'data': []}
    params = ['cluster_name', 'server_name', 'my_root_pw', 'auth_key']
   
    # parse input data
    try:
        data = request.json
    except ValueError:
        response.status = 400
        response.set_header("Content-Type", 'application/json')
        result['errors'].append('Value error, only application/json objects acepted')
        return json.dumps(result, indent=4, sort_keys=True)
    
    
    for key in data.keys():
        if key not in params:
            response.status = 400
            response.set_header("Content-Type", 'application/json')
            result['errors'].append('{} params not acepted'.format(key))
            return json.dumps(result, indent=4, sort_keys=True)
    
    for value in params:
        data[value] = data.get(value, '')
    
    if not data['auth_key'] or data['auth_key'] != 'CHANGE_ME':
        response.status = 401
        response.set_header("Content-Type", 'application/json')
        result['errors'].append('access denied')
        return json.dumps(result, indent=4, sort_keys=True)

    cluster_result = db_api.get_server_id(data)
    if cluster_result.get('errors'):
        response.status = 500
        response.set_header("Content-Type", 'application/json')
        result['errors'].extend(str(cluster_result['errors']))
        return json.dumps(result, indent=4, sort_keys=True)

    # return 200 Success
    response.set_header("Content-Type", 'application/json')
    return json.dumps(cluster_result, indent=4, sort_keys=True)

### END API-REST ###

if __name__ == '__main__':
    run(app, host='0.0.0.0', port=main_config.get('http_port', 8080), reloader=main_config['enable_reloader'], debug=main_config['enable_debug'])