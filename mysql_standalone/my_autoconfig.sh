generate_server_id_data() {
	cat <<-EOF
	{
		"auth_key":"$OPERATOR_SECRET", "cluster_name": "$CLUSTER_NAME", "server_name": "$MYSQL_HOSTNAME", "my_root_pw": "$MYSQL_ROOT_PASSWORD" 
	}
	EOF
}

generate_cluster_members_data() {
	cat <<-EOF
	{
		"auth_key":"$OPERATOR_SECRET", "cluster_name": "$CLUSTER_NAME", "operator_user": "$OPERATOR_USER", "operator_pw": "$OPERATOR_PASSWORD", "replica_user": "$REPLICA_USER", "replica_pw": "$REPLICA_PASSWORD"
	}
	EOF
}

mysql_autoconfig() {
	# MySQL autoconfig

	MYSQL_HOSTNAME=$(hostname)
	export MYSQL_HOSTNAME
	my_cnf=/etc/mysql/conf.d/mysqld.cnf
	# my_cnf=/tmp/mysqld.cnf
	if ! grep -Fq group_replication_group_name $my_cnf; then
		
		mysql_note "Run autoconfig: " 

		init_cluster=$(curl -s --header "Content-Type: application/json"   --request POST   \
		--data "$(generate_cluster_members_data)" \
		$OPERATOR_HOST/api/get/init_cluster)

		GR_NAME=$(echo "$init_cluster" | jq -r '.data.gr_name')
		GR_VCU=$(echo "$init_cluster" | jq -r '.data.gr_vcu')

		echo $GR_NAME
		echo $GR_VCU
		
		available_servers=$(curl --header "Content-Type: application/json"   --request POST   \
		--data "$(generate_cluster_members_data)" \
		$OPERATOR_HOST/api/get/cluster_members | jq -r '.data.available_servers')
		
		server_id=$(curl --header "Content-Type: application/json"   --request POST   \
				--data "$(generate_server_id_data)" \
				$OPERATOR_HOST/api/get/server_id | jq -r '.data.server_id')
		
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
			cluster_members=$(curl --header "Content-Type: application/json"   --request POST   \
			--data "$(generate_cluster_members_data)" \
			$OPERATOR_HOST/api/get/cluster_members | jq -r '.data.members[]')
			for server in $cluster_members
			do
				GR_SEEDS="$GR_SEEDS$server:33061,"
			done
			GR_SEEDS=$(echo $GR_SEEDS | sed 's/,$//')
		fi

		export GR_BOOTSTRAP
		export MYSQL_SERVER_ID
		export GR_SEEDS
		export GR_NAME
		export GR_VCU

		defined_envs=$(printf '${%s} ' $(env | cut -d= -f1))
		envsubst "$defined_envs" < /usr/local/bin/my.cnf.tpl > "$my_cnf"
		cp $my_cnf $DATADIR/my.cnf_init

		mysql_note "End autoconfig" 
	fi
}

mysql_autoconfig
