#!/bin/bash
set -eo pipefail
shopt -s nullglob

# logging functions
mysql_log() {
	local type="$1"; shift
	# accept argument string or stdin
	local text="$*"; if [ "$#" -eq 0 ]; then text="$(cat)"; fi
	local dt; dt="$(date --rfc-3339=seconds)"
	printf '%s [%s] [Entrypoint]: %s\n' "$dt" "$type" "$text"
}
mysql_note() {
	mysql_log Note "$@"
}
mysql_warn() {
	mysql_log Warn "$@" >&2
}
mysql_error() {
	mysql_log ERROR "$@" >&2
	exit 1
}


generate_server_id_data() {
	cat <<-EOF
	{
		"auth_key":"CHANGE_ME", "gr_name": "$GROUP_REPLICATION_NAME", "server_name": "$MYSQL_HOSTNAME"
	}
	EOF
}

generate_cluster_members_data() {
	cat <<-EOF
	{
		"auth_key":"CHANGE_ME", "gr_name": "$GROUP_REPLICATION_NAME"
	}
	EOF
}

mysql_autoconfig() {
	# MySQL autoconfig

	MYSQL_HOSTNAME=$(hostname)
	export MYSQL_HOSTNAME
	my_cnf=/etc/mysql/conf.d/mysqld.cnf
	# my_cnf=/tmp/mysqld.cnf

	if [ ! -f $my_cnf ]; then
		mysql_note "Run autoconfig: " 

		available_servers=$(curl -s --header "Content-Type: application/json"   --request POST   \
		--data "$(generate_cluster_members_data)" \
		http://operator:8080/api/get/cluster_members | jq -r '.data.available_servers')
		
		server_id=$(curl -s --header "Content-Type: application/json"   --request POST   \
				--data "$(generate_server_id_data)" \
				http://operator:8080/api/get/server_id | jq -r '.data.server_id')
		
		MYSQL_SERVER_ID=$server_id
		echo $available_servers
		echo $server_id
		
		if [ $available_servers -eq 0 ]; then
			echo "Bootstrap"
			GR_BOOTSTRAP="group_replication_bootstrap_group=on"
			GR_SEEDS=""
		else
			GR_BOOTSTRAP="group_replication_bootstrap_group=off"
			GR_SEEDS="group_replication_group_seeds="
			cluster_members=$(curl -s --header "Content-Type: application/json"   --request POST   \
			--data "$(generate_cluster_members_data)" \
			http://operator:8080/api/get/cluster_members | jq -r '.data.members[]')
			for server in $cluster_members
			do
				GR_SEEDS="$GR_SEEDS$server:33061,"
			done
			GR_SEEDS=$(echo $GR_SEEDS | sed 's/,$//')
		fi
		export GR_BOOTSTRAP
		export MYSQL_SERVER_ID
		export GR_SEEDS
		defined_envs=$(printf '${%s} ' $(env | cut -d= -f1))
		envsubst "$defined_envs" < /usr/local/bin/my.cnf.tpl > "$my_cnf"
		cp $my_cnf $DATADIR/my.cnf_init

		mysql_note "End autoconfig" 
	fi
}

mysql_autoconfig