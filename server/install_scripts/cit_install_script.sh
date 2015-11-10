#!/bin/bash
# Set server version number.
#export SERVER_VERSION='2.1.9'

rsync -e "ssh -o StrictHostKeyChecking=no" -avP segments-backup.ligo.org:.bashrc .
rsync -e "ssh -o StrictHostKeyChecking=no" -avP segments-backup.ligo.org:.pythonrc .
rsync -e "ssh -o StrictHostKeyChecking=no" -avP segments-backup.ligo.org:.vimrc .

yum -y install git
yum -y install ecp-cookie-init

git config --global http.cookiefile /tmp/ecpcookie.u`id -u`
git config --global user.email ryan.fisher@ligo.org
git config --global user.name "Ryan Fisher"

# Install Apache server.
yum -y install httpd

# Install Apache WSGI module.
yum -y install mod_wsgi


# Install MySQL.
yum -y install mysql-server

# Start MySQL server.
#service mysqld start
/etc/init.d/mysqld restart
chkconfig mysqld on

# Install PHP (for web interface).
yum -y install php php-mysql

yum -y install mod_ssl

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
cd ~/
git clone https://github.com/ligovirgo/dqsegdb.git
#curl http://10.20.5.14/repos/segdb/dqsegdb/$SERVER_VERSION/src.tar > src.tar
#mv src.tar /opt/dqsegdb/python_server/src/
cd /opt/dqsegdb/python_server/src/
cp ~/dqsegdb/server/src/* .

# Change dir.
cd /root

# Add WSGI script alias to Apache configuration file.
echo "WSGIScriptAlias / /opt/dqsegdb/python_server/src/application.py" >> /etc/httpd/conf.d/wsgi.conf

# Add Web Interface configuration.
echo "Alias /dqsegdb_web /usr/share/dqsegdb_web" >> /etc/httpd/conf.d/dqsegdb_web.conf

# Configure application Apache:
#curl http://10.20.5.14/repos/segdb/dqsegdb/dqsegdb5_example.conf > dqsegdb.conf
#/bin/cp dqsegdb.conf /etc/httpd/conf.d/

#cd ~
#rsync -avP sugar.phy.syr.edu:/home/rpfisher/dqsegdb5_backups_Jul272015 .

cd /etc/httpd/
mv conf.d conf.d.bck.$(date +%y%m%d)
rsync -e "ssh -o StrictHostKeyChecking=no" -avP segments-backup.ligo.org:/etc/httpd/conf.d .

int_addr=`ifconfig eth0 |sed -n 's/.*inet addr:\([0-9\.]*\).*/\1/p'`

ext_addr=`ifconfig eth1 |sed -n 's/.*inet addr:\([0-9\.]*\).*/\1/p'` 

server_name=`hostname -f`

sed -i "s/segments-backup\.ligo\.org/${server_name}/g" /etc/httpd/conf.d/dqsegdb.conf

sed -i "s/131\.215\.113\.158/${ext_addr}/g" /etc/httpd/conf.d/dqsegdb.conf

sed -i "s/10\.14\.0\.105/${int_addr}/g" /etc/httpd/conf.d/dqsegdb.conf

# Install M2Crypto library.
yum -y install m2crypto

# Setup ODBC Data Source Name (DSN)
echo "[DQSEGDB]
DRIVER=MySQL
DATABASE=dqsegdb-backup
USER=dqsegdb_user
PASSWORD=Q6a6jS6L63RtqnDm" >> /etc/odbc.ini

# Install repo for phpMyAdmin.
yum -y install http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm

# Install phpMyAdmin
yum -y install phpmyadmin
cd /etc/phpMyAmin
mv /etc/phpMyAdmin/config.inc.php /etc/phpMyAdmin/config.inc.php.bck.$(date +%y%m%d)
rsync -e "ssh -o StrictHostKeyChecking=no" -avP segments-backup.ligo.org:/etc/phpMyAdmin/config.inc.php .

# Fix default httpd/conf dir
mv /etc/httpd/conf /etc/httpd/conf.bck.$(date +%y%m%d)
cd /etc/httpd
rsync -e "ssh -o StrictHostKeyChecking=no" -avP segments-backup.ligo.org:/etc/httpd/conf .

mv /etc/init.d/httpd /etc/init.d/httpd.bck.$(date +%y%m%d)
cd /etc/init.d/
rsync -e "ssh -o StrictHostKeyChecking=no" -avP segments-backup.ligo.org:/etc/init.d/httpd .

# Import data and create main database.
#curl http://10.20.5.14/repos/segdb/dqsegdb/dqsegdb.sql > dqsegdb.sql
#mysql -e "DROP DATABASE IF EXISTS dqsegdb"
#mysql -e "CREATE DATABASE dqsegdb"
#mysql -e "use dqsegdb"
#mysql dqsegdb < dqsegdb.sql


# Create database users.
mysql -e "CREATE USER 'dqsegdb_user'@'localhost' IDENTIFIED BY 'Q6a6jS6L63RtqnDm'"
mysql -e "CREATE USER 'admin'@'localhost' IDENTIFIED BY 'lvdb_11v35'"

# Give user privileges on the database.
mysql -e "GRANT SELECT, INSERT, UPDATE ON dqsegdb.* TO 'dqsegdb_user'@'localhost'"
mysql -e "GRANT ALL PRIVILEGES ON * . * TO 'admin'@'localhost'"

# Try to import a backup of primary database
rsync -e "ssh -o StrictHostKeyChecking=no" -avP segments-backup.ligo.org:bin ~/
cd ~/bin
/bin/bash populate_from_backup.sh

# move certs to appopriate locations, as referenced by /etc/httpd/conf.d/dqsegdb
cp /etc/pki/tls/certs/localhost.crt /etc/pki/tls/certs/localhost.crt.old.$(date +%y%m%d)
cp /etc/pki/tls/private/localhost.key /etc/pki/tls/private/localhost.key.bck.$(date +%y%m%d)
# NOTE:  NEXT TWO LINES ASSUME KEY/CERT PAIR ARE IN LOCATION /ETC/GRID-SECURITY!
cp /etc/grid-security/*.ligo.org.pem /etc/pki/tls/certs/localhost.crt 
cp /etc/grid-security/*.ligo.org.key /etc/pki/tls/private/localhost.key

# Get all cert identifier packages:
yum -y install cilogon-ca-certs
yum -y install osg-ca-certs
yum -y install ligo-ca-certs

# Start Apache server.
chkconfig httpd on
/etc/init.d/httpd restart


