from mongoengine import *
import datetime
import uuid

class Cluster(Document):
    cluster_name = StringField(required=False, unique=True, default=uuid.uuid4().hex)
    gr_name = StringField(required=True, unique=True)
    state = StringField(required=False, default='discovered')
    created_time = DateTimeField(default=datetime.datetime.utcnow)
    modified_time = DateTimeField(default=datetime.datetime.utcnow)

class Server(Document):
    cluster = ReferenceField(Cluster)
    server_id = IntField(required=True, unique_with='cluster')
    server_name = StringField(required=True)
    created_time = DateTimeField(default=datetime.datetime.utcnow)
    modified_time = DateTimeField(default=datetime.datetime.utcnow)

class ClusterId(Document):
    last_id = IntField(required=True)
    cluster = ReferenceField(Cluster)
    created_time = DateTimeField(default=datetime.datetime.utcnow)
    modified_time = DateTimeField(default=datetime.datetime.utcnow)