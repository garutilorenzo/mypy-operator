## WARNING Autogenerted file
## Please don't edit, remove this file

[mysqld]

#skip-ssl

server-id = ${MYSQL_SERVER_ID}
port      = 3306

binlog_format = ROW

gtid_mode=ON
enforce-gtid-consistency=ON

log_replica_updates
log_bin                   = mysql-bin

default_storage_engine = InnoDB

# replication

report-host = ${MYSQL_HOSTNAME}
replica_net_timeout = 60

skip_replica_start

transaction_isolation = 'READ-COMMITTED'

binlog_checksum = NONE
relay_log_info_repository = TABLE
transaction_write_set_extraction = XXHASH64

auto_increment_increment = 1
auto_increment_offset = 2

binlog_transaction_dependency_tracking = WRITESET 
replica_parallel_type = LOGICAL_CLOCK
replica_preserve_commit_order = ON