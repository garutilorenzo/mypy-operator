#!/bin/bash

set -e

BASE_PATH=/app/mysqlrouter

if [ "$1" = 'mysqlrouter' ]; then
	if [[ -z $MYSQL_HOST || -z $MYSQL_USER || -z $MYSQL_PASSWORD || -z $MYSQL_ROUTER_USER ]]; then
		echo "We require all of"
		echo "    MYSQL_HOST"
		echo "    MYSQL_USER"
		echo "    MYSQL_PASSWORD"
		echo "    MYSQL_ROUTER_USER"
		echo "to be set. Exiting."
		exit 1
	fi

	if [[ -z $MYSQL_PORT ]]; then
		MYSQL_PORT=3306
	fi

	PASSFILE=$(mktemp)
	echo "$MYSQL_PASSWORD" > "$PASSFILE"
	DEFAULTS_EXTRA_FILE=$(mktemp)
	cat >"$DEFAULTS_EXTRA_FILE" <<-EOF
	[client]
	password="$MYSQL_PASSWORD"
	EOF
	unset MYSQL_PASSWORD
	until mysql --defaults-extra-file="$DEFAULTS_EXTRA_FILE" -h "$MYSQL_HOST" -P"$MYSQL_PORT" -u "$MYSQL_USER" -nsLNE -e 'exit'; do
	  >&2 echo "MySQL is unavailable - sleeping"
	  sleep 5
	done

	echo "Succesfully contacted mysql server at $MYSQL_HOST. Checking for cluster state."
	if ! [[ "$(mysql --defaults-extra-file="$DEFAULTS_EXTRA_FILE" -u "$MYSQL_USER" -h "$MYSQL_HOST" -P "$MYSQL_PORT" -e "show status;" 2> /dev/null)" ]]; then
		echo "Can not connect to database. Exiting."
		exit 1
	fi

	echo "Check if config exist"
	if [ -f "$BASE_PATH/mysqlrouter.key" ]; then
	   echo "Config found."
	   echo "Start mysqlrouter"
	   exec "$@" --config $BASE_PATH/mysqlrouter.conf
	else 
		echo "Succesfully contacted mysql server at $MYSQL_HOST. Trying to bootstrap."
		mysqlrouter --bootstrap "$MYSQL_USER@$MYSQL_HOST:$MYSQL_PORT" --user=mysqlrouter --directory $BASE_PATH --account $MYSQL_ROUTER_USER  --force < "$PASSFILE"
		sed -i -e 's/logging_folder=.*$/logging_folder=/' $BASE_PATH/mysqlrouter.conf
		echo "Starting mysql-router."
		exec "$@" --config $BASE_PATH/mysqlrouter.conf
	fi
fi

rm -f "$PASSFILE"
rm -f "$DEFAULTS_EXTRA_FILE"
unset DEFAULTS_EXTRA_FILE

exec "$@"