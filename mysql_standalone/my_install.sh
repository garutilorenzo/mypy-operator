#!/bin/bash

mkdir -p /etc/my-operator

if [ ! -f /etc/my-operator/operator.conf ]; then
	echo "operator.conf not found"
	echo "I will download a sample operator.conf"
	echo "PLEASE adjust this file with your settings"
	exit 1
fi

echo "WARNING!!"
echo "This install script will REMOVE ALL the data"
echo "under your MySQL data dir"
echo "WARNING!!"

read -r -p "Are you sure? [Y/n]" response
echo ""
response=${response,,}
if [[ $response =~ ^(yes|y| ) ]] || [[ -z $response ]]; then

	DEBIAN_FRONTEND=noninteractive

	apt-get update
	apt-get install -y --no-install-recommends mysql-server-8.0

	systemctl stop mysql

	cat <<-EOF > /etc/mysql/mysql.conf.d/native_pw.cnf
	[mysqld]
	default-authentication-plugin=mysql_native_password
	EOF

	source /usr/local/bin/my_init.sh

	docker_setup_env mysqld

	rm -rf $DATADIR
	mkdir $DATADIR
	mkdir -p /var/run/mysqld/
	chown -R mysql:mysql $DATADIR
	chown -R mysql:mysql /var/run/mysqld/

	/usr/local/bin/my_init.sh mysqld

	mkdir -p /etc/systemd/system/mysql.service.d
	cat <<-EOF > /etc/systemd/system/mysql.service.d/my_autoconfig.conf
	[Service]
	ExecStartPre=/usr/local/bin/my_autoconfig.sh
	EOF

	systemctl daemon-reload
else
	echo "Exit"
	exit 1
fi