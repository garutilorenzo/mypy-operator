import socket

class StaticPage(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url

def build_meta(page_name=None, title=None):
    if title:
        title = title[:80]
        description = title[:150]
    elif page_name:
        title = description = META_COSTRAINT['base_page'].format(page_name)
    else:
        title = description = META_COSTRAINT['base']
    meta = Meta(title=title, description=description)
    return meta

def build_nav_pages():
    pages = []
    
    pages_list = [
        ('Home', '/'),
        ('Clusters', '/clusters'),
        ('Servers', '/servers'),
    ]
    
    for page in pages_list:
        item = StaticPage(name=page[0], url=page[1])
        pages.append(item)
    
    return pages

def build_nav_dropdown_pages():
    pages = []
    
    pages_list = [
        ('Docs', '/docs'),
    ]
    
    for page in pages_list:
        item = StaticPage(name=page[0], url=page[1])
        pages.append(item)
    
    return pages

def is_server_reachable(server_name, mysql_port=3306):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((server_name, mysql_port))
        s.close()
        result = True
    except Exception as e:
        s.close()
        result = False
    return result