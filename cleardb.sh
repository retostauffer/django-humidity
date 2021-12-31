#!/bin/bash


# Development stuff; not the real db/password.
exe="mysql -u django -pdjango django"
for table in $($exe -e 'show tables'); do
    n=`echo $table | egrep "^djangohumidity_" | wc -l`
    if [ $n -eq 1 ] ; then
        $exe -e "SET FOREIGN_KEY_CHECKS = 0; DROP TABLE ${table}; SET FOREIGN_KEY_CHECKS = 1;"
    fi

done
