from mongoengine import *
import datetime

class Cluster(Document):
    cluster_name = StringField(required=False, unique=True)
    gr_name = StringField(required=True, unique=True)
    gr_vcu = StringField(required=True, unique=True)
    state = StringField(required=False, default='discovered')
    replica_user = StringField(required=True, default='replica')
    replica_pw = StringField(required=True)
    operator_user = StringField(required=True, default='operator')
    operator_pw = StringField(required=True)
    created_time = DateTimeField(default=datetime.datetime.utcnow)
    modified_time = DateTimeField(default=datetime.datetime.utcnow)

class Server(Document):
    cluster = ReferenceField(Cluster)
    server_id = IntField(required=True, unique_with='cluster')
    server_name = StringField(required=True)
    root_pw = StringField(required=True)
    created_time = DateTimeField(default=datetime.datetime.utcnow)
    modified_time = DateTimeField(default=datetime.datetime.utcnow)

class ClusterId(Document):
    last_id = IntField(required=True)
    cluster = ReferenceField(Cluster)
    created_time = DateTimeField(default=datetime.datetime.utcnow)
    modified_time = DateTimeField(default=datetime.datetime.utcnow)