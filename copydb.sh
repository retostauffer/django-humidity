#!/bin/bash

FILE="my.cnf"
LOCAL_DB=`cat $FILE | egrep "database" | awk '{print $3}'`
LOCAL_USER=`cat $FILE | egrep "user" | awk '{print $3}'`
LOCAL_PASS=`cat $FILE | egrep "password" | awk '{print $3}'`

# retostauffer.org readonly db pass
REMOTE_PASS=`secret-tool lookup server retostauffer.org service mysql`

ssh retostauffer "mysqldump -u stauffer -p'${REMOTE_PASS}' stauffer_djangohumidity" > _dump.sql
mysql -u ${LOCAL_USER} -p${LOCAL_PASS} ${LOCAL_DB} < _dump.sql && rm _dump.sql
