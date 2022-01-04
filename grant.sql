CREATE USER 'orc_client_user'@'%' IDENTIFIED BY 'orc_client_password';
GRANT SUPER, PROCESS, REPLICATION SLAVE, REPLICATION CLIENT, RELOAD ON *.* TO 'orc_client_user'@'%';
GRANT SELECT ON mysql.slave_master_info TO 'orc_client_user'@'%';
GRANT SELECT ON meta.* TO 'orc_client_user'@'%';
GRANT SELECT ON performance_schema.replication_group_members TO 'orc_client_user'@'%';