# Copyright (C) 2014-2020 Syracuse University, European Gravitational Observatory, and Christopher Newport University.  Written by Ryan Fisher and Gary Hemming. See the NOTICE file distributed with this work for additional information regarding copyright ownership.

# This program is free software: you can redistribute it and/or modify

# it under the terms of the GNU Affero General Public License as

# published by the Free Software Foundation, either version 3 of the

# License, or (at your option) any later version.

#

# This program is distributed in the hope that it will be useful,

# but WITHOUT ANY WARRANTY; without even the implied warranty of

# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the

# GNU Affero General Public License for more details.

#

# You should have received a copy of the GNU Affero General Public License

# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#!/bin/bash
# Set server version number.
export SERVER_VERSION='2.1.9'

# Install Apache server.
yum -y install httpd

# Install Apache WSGI module.
yum -y install mod_wsgi

yum -y install mod_ssl

# Start Apache server.
chkconfig httpd on
/etc/init.d/httpd start
#service httpd start

# Install MySQL.
yum -y install mysql-server

# Start MySQL server.
#service mysqld start
/etc/init.d/mysqld restart
chkconfig mysqld on

# Install PHP (for web interface).
yum -y install php php-mysql

# Install pyodbc library for Python. N.B. This also installs unixODBC as a
# dependency.
yum -y install pyodbc

# By default, unixODBC only installs PostGreSQL connector libraries. Install
# the MySQL connectors now.
yum -y install mysql-connector-odbc

# Increase innodb buffer pool size.
echo "[mysqld]" >> /etc/my.cnf
echo "innodb_buffer_pool_size = 40G" >> /etc/my.cnf

# Make DQSEGDB server directories
cd /opt
mkdir dqsegdb
cd dqsegdb
mkdir python_server
cd python_server
mkdir logs
chmod 777 logs
#mkdir $SERVER_VERSION
#cd $SERVER_VERSION
#mkdir cache
#chmod 777 cache
mkdir src
cd src

# Add server files.
curl http://10.20.5.14/repos/segdb/dqsegdb/$SERVER_VERSION/src.tar > src.tar
mv src.tar /opt/dqsegdb/python_server/src/
cd /opt/dqsegdb/python_server/src/
tar -xvf src.tar 

# Change dir.
cd /root

# Add WSGI script alias to Apache configuration file.
echo "WSGIScriptAlias / /opt/dqsegdb/python_server/src/application.py" >> /etc/httpd/conf.d/wsgi.conf

# Add Web Interface configuration.
echo "Alias /dqsegdb_web /usr/share/dqsegdb_web" >> /etc/httpd/conf.d/dqsegdb_web.conf

# Configure application Apache:
curl http://10.20.5.14/repos/segdb/dqsegdb/dqsegdb5_example.conf > dqsegdb.conf
/bin/cp dqsegdb.conf /etc/httpd/conf.d/

int_addr=`ifconfig eth0 |sed -n 's/.*inet addr:\([0-9\.]*\).*/\1/p'`

ext_addr=`ifconfig eth1 |sed -n 's/.*inet addr:\([0-9\.]*\).*/\1/p'` 

server_name=`hostname`

sed -i "s/dqsegdb4\.phy\.syr\.edu/${server_name}/g" /etc/httpd/conf.d/dqsegdb.conf

sed -i "s/128\.230\.190\.57/${ext_addr}/g" /etc/httpd/conf.d/dqsegdb.conf

sed -i "s/10\.20\.5\.43/${int_addr}/g" /etc/httpd/conf.d/dqsegdb.conf

# Install M2Crypto library.
yum -y install M2Crypto

# Restart Apache.
/etc/init.d/httpd restart
#service httpd restart

# Setup ODBC Data Source Name (DSN)
echo "[DQSEGDB]
DRIVER=MySQL
DATABASE=dqsegdb" >> /etc/odbc.ini

# Install repo for phpMyAdmin.
yum install http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm

# Install phpMyAdmin
yum -y install phpmyadmin
curl http://10.20.5.14/repos/segdb/dqsegdb/config_inc_php.txt > config.inc.php
/bin/cp config.inc.php /etc/phpMyAdmin/
curl http://10.20.5.14/repos/segdb/dqsegdb/phpMyAdmin.conf > phpMyAdmin.conf
/bin/cp phpMyAdmin.conf /etc/httpd/conf.d/
curl http://10.20.5.14/repos/segdb/dqsegdb/httpd > httpd
/bin/cp httpd /etc/init.d/

# Import data and create main database.
curl http://10.20.5.14/repos/segdb/dqsegdb/dqsegdb.sql > dqsegdb.sql
mysql -e "DROP DATABASE IF EXISTS dqsegdb"
mysql -e "CREATE DATABASE dqsegdb"
mysql -e "use dqsegdb"
mysql dqsegdb < dqsegdb.sql


# Give user privileges on the database.
mysql -e "GRANT SELECT, INSERT, UPDATE ON dqsegdb.* TO 'dqsegdb_user'@'localhost'"
mysql -e "GRANT ALL PRIVILEGES ON * . * TO 'admin'@'localhost'"

# Set up iptables
curl http://10.20.5.14/repos/segdb/dqsegdb/iptables.default.Mar132014 > iptables.default.Mar132014
iptables-restore < iptables.default.Mar132014
/etc/init.d/iptables save
service iptables restart
service httpd restart
