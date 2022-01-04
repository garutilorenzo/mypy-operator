#!/bin/bash

MYSQL_PORT=3306

help(){
	echo ""
	echo "cluster.sh -h <MYSQL_HOST> -u <MYSQL_USER> -p <MYSQL_ROOT_PASSWORD> -c <CLUSTER_NAME>"
	echo "optional parameter: -P <MYSQL_PORT>"
}

parse_opts(){

	while getopts "h:Pu:p:c:" opt; do
		case $opt in
			h)
			MYSQL_HOST=$OPTARG
			;;
			P)
			MYSQL_PORT=$OPTARG
			;;
			u)
			MYSQL_USER=$OPTARG
			;;
			p)
			MYSQL_ROOT_PASSWORD=$OPTARG
			;;
			c)
			CLUSTER_NAME=$OPTARG
			;;
			\?)
			echo "Invalid option: -$OPTARG" >&2
			help
			exit 1
			;;
		esac
	done
}

validate_opts(){

	if [ -z ${MYSQL_HOST} ] || [ -z ${MYSQL_USER} ] || [ -z ${MYSQL_ROOT_PASSWORD} ] || [ -z ${CLUSTER_NAME} ] 
	then
		echo "Missing parameters"
		help
		exit 1
	fi 

}

cluster_init() {
	HOSTPORT=$(mysql --no-defaults -h "$MYSQL_HOST" -P"$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_ROOT_PASSWORD" -nsLNE -e "select CONCAT(member_host, ':', member_port) as primary_host from performance_schema.replication_group_members where member_state='ONLINE' and member_id=(IF((select @grpm:=variable_value from performance_schema.global_status where variable_name='group_replication_primary_member') = '', member_id, @grpm)) limit 1" 2>/dev/null | grep -v '*')
	echo $HOSTPORT
	metadata_exists=$(mysqlsh --uri="$MYSQL_USER"@"$MYSQL_HOST":"$MYSQL_PORT" -p"$MYSQL_ROOT_PASSWORD" --no-wizard --js -i -e "dba.getCluster( '${CLUSTER_NAME}' )" 2>&1 | grep "<Cluster:$CLUSTER_NAME>")
	
	echo $metadata_exists

	if [ -z "$metadata_exists" ]; then
		# Then let's create the innodb cluster metadata
		output=$(mysqlsh --uri="$MYSQL_USER"@"$HOSTPORT" -p"$MYSQL_ROOT_PASSWORD" --no-wizard --js -i -e "dba.createCluster('${CLUSTER_NAME}', {adoptFromGR: true})")
	fi
}

parse_opts $@
validate_opts
cluster_init