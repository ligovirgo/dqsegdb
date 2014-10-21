#!/bin/bash
# Set server version number.
export SERVER_VERSION='v1r13'

# Install Apache server.
yum -y install httpd

# Install Apache WSGI module.
yum -y install mod_wsgi

# Start Apache server.
chkconfig httpd on
#/etc/init.d/httpd start
service httpd start

# Install MySQL.
wget http://dev.mysql.com/get/mysql-community-release-el6-5.noarch.rpm/from/http://repo.mysql.com/
yum install -y mysql-community-release-el6-5.noarch.rpm
#yum -y install mysql-server

# Start MySQL server.
service mysqld start
chkconfig mysqld on

# Install PHP (for web interface).
install php php-mysql

# Install pyodbc library for Python. N.B. This also installs unixODBC as a
# dependency.
yum -y install pyodbc

# By default, unixODBC only installs PostGreSQL connector libraries. Install
# the MySQL connectors now.
yum -y install mysql-connector-odbc

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
curl http://10.20.1.26/repos/segdb/dqsegdb/$SERVER_VERSION/src.tar > src.tar
mv src.tar /opt/dqsegdb/python_server/src/
cd /opt/dqsegdb/python_server/src/
tar -xvf src.tar 
cd /root

# Add WSGI script alias to Apache configuration file.
echo "WSGIScriptAlias / /opt/dqsegdb/python_server/src/application.py" >> /etc/httpd/conf.d/wsgi.conf

# Restart Apache.
#Restart Apache: /etc/init.d/httpd restart
service httpd restart

# Setup ODBC Data Source Name (DSN)
echo "[DQSEGDB]
DRIVER=MySQL
DATABASE=dqsegdb
USER=dqsegdb_user
PASSWORD=Q6a6jS6L63RtqnDm" >> /etc/odbc.ini

# Install repo for phpMyAdmin.
yum install http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm

# Install phpMyAdmin
yum -y install phpmyadmin
curl http://10.20.1.26/repos/segdb/dqsegdb/config_inc_php.txt > config.inc.php
/bin/cp config.inc.php /etc/phpMyAdmin/
curl http://10.20.1.26/repos/segdb/dqsegdb/phpMyAdmin.conf > phpMyAdmin.conf
/bin/cp phpMyAdmin.conf /etc/httpd/conf.d/
curl http://10.20.1.26/repos/segdb/dqsegdb/httpd > httpd
/bin/cp httpd /etc/init.d/

# Import data
curl http://10.20.1.26/repos/segdb/dqsegdb/dqsegdb.sql > dqsegdb.sql
mysql -e "DROP DATABASE IF EXISTS dqsegdb"
mysql -e "CREATE DATABASE dqsegdb"
mysql -e "use dqsegdb"
mysql dqsegdb < dqsegdb.sql

# Create database users.
mysql -e "CREATE USER 'dqsegdb_user'@'localhost' IDENTIFIED BY 'Q6a6jS6L63RtqnDm'"
mysql -e "CREATE USER 'admin'@'localhost' IDENTIFIED BY 'lvdb_11v35'"

# Give user privileges on the database.
mysql -e "GRANT SELECT, INSERT, UPDATE ON dqsegdb.* TO 'dqsegdb_user'@'localhost'"
mysql -e "GRANT ALL PRIVILEGES ON * . * TO 'admin'@'localhost'"

# Set up iptables
curl http://10.20.1.26/repos/segdb/dqsegdb/iptables.default.Mar132014 > iptables.default.Mar132014
iptables-restore < iptables.default.Mar132014
/etc/init.d/iptables save
service iptables restart
service httpd restart


