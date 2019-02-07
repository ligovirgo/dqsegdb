#!/bin/bash

# This is a script to set up one of the data quality segments database (DQsegDB) machines.
# Warning: This script assumes that it is being run by user root.  Installation by any other user will likely produce errors.

# set host; valid options: segments, segments-backup, segments-web, segments-dev, segments-dev2, segments-s6, segments-other
host="segments-backup"
if [ $host != "segments" ] && [ $host != "segments-backup" ] && [ $host != "segments-web ] && [ $host != "segments-dev" ] && [ $host != "segments-dev2 ] \
    && [ $host != "segments-s6" ] && [ $host != "segments-other" ]
then
  echo "### ERROR ### Variable 'host' is not set to a valid value.  Please fix this and run this script again."
  exit
fi

# The default is to create a 'live' system, with all services, cron jobs, etc. ready to run immediately;
#    if you don't want that, change the 'live' variable to 0 before running this script.
# If 'live' is not 1, some services will be started to set them up, then shut down after that.
# NOTE: This doesn't apply to mariadb and httpd yet.
#       They will be started, no matter what.  We'll work on making that optional later.
live=1


# make backups of user root config files (if they exist) and then import new files
cd /root/ 
if [ -e ./.bashrc ]; then cp  ./.bashrc  ./.bashrc_$(date +%Y.%m.%d).bak ; fi
if [ -e ./.vimrc ]; then cp  ./.vimrc  ./.vimrc_$(date +%Y.%m.%d).bak ; fi
if [ -e ./.pythonrc ]; then cp  ./.pythonrc  ./.pythonrc_$(date +%Y.%m.%d).bak ; fi
#rsync -avP /backup/segdb/segments/install_support/.bashrc .
#rsync -avP /backup/segdb/segments/install_support/.vimrc .
#rsync -avP /backup/segdb/segments/install_support/.pythonrc .
rsync -avP /backup/segdb/reference/install_support/.bashrc .
rsync -avP /backup/segdb/reference/install_support/.vimrc .
rsync -avP /backup/segdb/reference/install_support/.pythonrc .
chown  root:root  .bashrc  .pythonrc  .vimrc
. ./.bashrc
mkdir /root/bin/

yum -y install git nano mlocate screen
mkdir dqsegdb_git
cd dqsegdb_git
git clone https://github.com/ligovirgo/dqsegdb.git  
cd dqsegdb/server/install_scripts
cat cit_install_script_sl7update.sh
echo "Installation script/instructions printed"

# used for connecting to git repositories with Kerberos (if this is still used)
yum -y install ecp-cookie-init
git config --global http.cookiefile /tmp/ecpcookie.u`id -u`
#git config --global user.email ryan.fisher@ligo.org
#git config --global user.name "Ryan Fisher"
git config --global user.email robert.bruntz@ligo.org
git config --global user.name "Robert Bruntz"
# these lines above might be changed to a different user later

# Set LGMM (LIGO Grid-Mapfile Manager) to run on reboot and start it now
cp  /backup/segdb/reference/lgmm/whitelist  /etc/grid-security/
touch /etc/grid-security/grid-mapfile
touch /etc/grid-security/whitelist   ### just in case the config file looks for it; missing expected file crashes lgmm
touch /etc/grid-security/blacklist   ### just in case the config file looks for it; missing expected file crashes lgmm
chown nobody:nobody /etc/grid-security/grid-mapfile
chmod 644 /etc/grid-security/grid-mapfile
/sbin/chkconfig lgmm on
systemctl restart lgmm


# Install Apache, MariaDB (successor to MySQL), PHPMyAdmin, etc.
# Install Apache server.
yum -y install httpd

# Install Apache WSGI module.
yum -y install mod_wsgi

# Install mariaDB, set it to run on startup, and start it
yum -y install mariadb-server mariadb mariadb-devel
### not started until later - b/c we want to change the buffer pool size first?

# Install PHP (for web interface).
yum -y install php php-mysql

yum -y install mod_ssl

# Install pyodbc library for Python. N.B. This also installs unixODBC as a dependency.
yum -y install pyodbc

# By default, unixODBC only installs PostGreSQL connector libraries. Install the MySQL connectors now.
yum -y install mysql-connector-odbc

# Increase innodb buffer pool size.
echo "[mysqld]" >> /etc/my.cnf
# set max_connections to 256 here? - do in /etc/mysql/my.cnf ?
if [ $host == "segments-dev2" ]
then
  echo "innodb_buffer_pool_size = 20G" >> /etc/my.cnf
else
  echo "innodb_buffer_pool_size = 40G" >> /etc/my.cnf
fi
### Note: 20 GB for segments-dev2 is b/c it has limited disk space; others should be fine.  (Maybe increase it for some/all others?)

#if [ $live -eq 1 ]
#then
#  systemctl enable mariadb.service
#  systemctl restart mariadb.service
#else
#  echo "### NOTICE ### The 'live' variable is not set to 1, so the mariadb service is not being started."
#fi
systemctl enable mariadb.service
systemctl restart mariadb.service


# Set up DQSegDB stuff
# Make DQSEGDB server directories
mkdir -p /opt/dqsegdb/python_server/logs
# maybe at some point change the above to /opt/dqsegdb/logs/python_server/, and change python code to match (or create a symlink), 
#    so that the code and logs are separate?
chmod 777 /opt/dqsegdb/python_server/logs
mkdir -p /opt/dqsegdb/python_server/src

# Add server files.
cd ~
git clone https://github.com/ligovirgo/dqsegdb.git
cp  ~/dqsegdb/server/src/*  /opt/dqsegdb/python_server/src/

# Add WSGI script alias to Apache configuration file.
echo "WSGIScriptAlias / /opt/dqsegdb/python_server/src/application.py" >> /etc/httpd/conf.d/wsgi.conf
### why is this done a few lines before the /etc/httpd/conf.d/ dir is moved and replaced???
### turns out that the file copied over later (/etc/httpd/conf.d/wsgi.conf) already has this line
### so the above line isn't needed at all; it just creates the file, which is then moved


## FIX!!! Replace with openssl!!!
# Install M2Crypto library.
yum -y install m2crypto
### some code uses m2crypto; need to change that code at the same time as (or before) changing this over to openssl

# Setup ODBC Data Source Name (DSN)
if [ $host == "segments" ] || [ $host == "segments-web" ] || [ $host == "segments-backup" ] || [ $host == "segments-dev" ]
then
  if [ -e /etc/odbc.ini ]; then mv  /etc/odbc.ini  /etc/odbc.ini_bak_$(date +%Y.%m.%d) ; fi
  cp  /backup/segdb/reference/root_files/$host/odbc.ini  /etc/
fi

# Install phpMyAdmin
### do we want to do this for every segments machine?
if [ $host == "segments" ] || [ $host == "segments-web" ] || [ $host == "segments-backup" ] || [ $host == "segments-dev" ]
then
  yum -y install phpmyadmin
  mv /etc/phpMyAdmin/config.inc.php   /etc/phpMyAdmin/config.inc.php.bck.$(date +%Y.%m.%d)
  rsync -avP /backup/segdb/reference/install_support/config.inc.php   /etc/phpMyAdmin/
  chown root:apache /etc/phpMyAdmin/config.inc.php
fi


# Configure application Apache:
# Fix default httpd/conf and httpd/conf.d dirs
### fixme01 fix!!!
mv /etc/httpd/conf     /etc/httpd/conf.bck.$(date +%Y.%m.%d)
mv /etc/httpd/conf.d   /etc/httpd/conf.d.bck.$(date +%Y.%m.%d)
if [ $host == "segments" ] || [ $host == "segments-dev" ]
then
  rsync -avP /backup/segdb/segments/install_support/conf.d   /etc/httpd/
  ### note: this part is probably wrong; it worked for segments-old, when it had Shibboleth installed, 
  ###       but it probably won't work for systems without Shibboleth
  ### we should start a new dir, with only the files that we need in it (from the files in the above dir)
  ### there should also be something to create/populate /etc/httpd/conf/
#  cp -r  /backup/segdb/reference/install_support/segments/etc_httpd_conf.d  /etc/httpd/
#  cp -r /backup/segdb/segments/install_support/conf_segments-dev_SL7/conf  /etc/httpd/
#  cp -r /backup/segdb/segments/install_support/conf.d_segments-dev_SL7/conf.d  /etc/httpd/
  if [ -e /etc/httpd/conf.d/shib.conf ]; then mv /etc/httpd/conf.d/shib.conf /etc/httpd/conf.d/shib.conf_nameblocked; fi
### the above are done in place of the rsync, to avoid the issue with shibboleth (b/c shibboleth is not installed on new systems by default)
fi
if [ $host == "segments-backup" ]
then
  cp -r  /backup/segdb/reference/install_support/segments-backup/etc_httpd_conf    /etc/httpd/conf/
  cp -r  /backup/segdb/reference/install_support/segments-backup/etc_httpd_conf.d  /etc/httpd/conf.d/
fi
if [ $host == "segments-web" ]
then
#  cp -r  /backup/segdb/reference/install_support/segments-web/etc_httpd_conf.d  /etc/httpd/
### note: this one isn't set up yet
  sleep 0   ### have to do *something*, or bash gets cranky
fi
chown -R root:root /etc/httpd/conf.d
chown -R root:root /etc/httpd/conf

# Get the IP addresses for (2 Ethernet ports? Are these special somehow?) and the hostname
#FIX!!! the Devices don't seem to have standard names on SL7?
# issue: on different systems, eth0 = eno1 = ens10 (10.14.xx.xx address); eth1 = eno2 = ens3 (131.215.xx.xx address)
# not all installations can use the following lines; the "grep "inet 10"" lines work on SL 7.5, but not 6.1 
int_addr=`ifconfig | grep "inet 10" | awk '{print $2}'`
#int_addr=`ifconfig ens10 | grep "inet " | awk '{print $2}'`
#int_addr=`ifconfig ens10 |sed -n 's/.*inet \([0-9\.]*\).*/\1/p'`
#int_addr=`ifconfig eno1 |sed -n 's/.*inet addr:\([0-9\.]*\).*/\1/p'`
ext_addr=`ifconfig | grep "inet 131" | awk '{print $2}'`
#ext_addr=`ifconfig ens3 | grep "inet " | awk '{print $2}'`
#ext_addr=`ifconfig ens3 |sed -n 's/.*inet \([0-9\.]*\).*/\1/p'`
#ext_addr=`ifconfig eno2 |sed -n 's/.*inet addr:\([0-9\.]*\).*/\1/p'` 
echo "internal network address =  $int_addr"
echo "external network address =  $ext_addr"
server_name=`hostname -f`
echo "server name =  $server_name"

# Replace the IP addresses and hostname in the dqsegdb config file
### this would be a good place to have separate blocks for each server - segments, segments-backup, segments-web, segments-dev, segments-dev2, segments-s6
cp /etc/httpd/conf.d/dqsegdb.conf /etc/httpd/conf.d/dqsegdb.conf_$(date +%Y.%m.%d).bak
if [ $host == "segments" ]
then
  sed -i "s/segments\.ligo\.org/${server_name}/g"   /etc/httpd/conf.d/dqsegdb.conf
  sed -i "s/131\.215\.113\.156/${ext_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf
  sed -i "s/10\.14\.0\.101/${int_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf
fi
if [ $host == "segments-backup" ]
then
  sed -i "s/segments\-backup\.ligo\.org/${server_name}/g"   /etc/httpd/conf.d/dqsegdb.conf
  sed -i "s/131\.215\.113\.158/${ext_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf
  sed -i "s/10\.14\.0\.105/${int_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf
fi
if [ $host == "segments-web" ]
then
  sed -i "s/segments\-web\.ligo\.org/${server_name}/g"   /etc/httpd/conf.d/dqsegdb.conf
  sed -i "s/131\.215\.125\.183/${ext_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf
  sed -i "s/10\.14\.0\.99/${int_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf
fi
if [ $host == "segments-dev" ]
then
  sed -i "s/segments\-dev\.ligo\.org/${server_name}/g"   /etc/httpd/conf.d/dqsegdb.conf
  sed -i "s/131\.215\.113\.159/${ext_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf
  sed -i "s/10\.14\.0\.106/${int_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf
fi
if [ $host == "segments-dev2" ]
then
  sed -i "s/segments\-dev2\.ligo\.org/${server_name}/g"   /etc/httpd/conf.d/dqsegdb.conf
  sed -i "s/131\.215\.125\.38/${ext_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf
  sed -i "s/10\.14\.0\.83/${int_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf
fi
if [ $host == "segments-s6" ]
then
  sed -i "s/segments\-s6\.ligo\.org/${server_name}/g"   /etc/httpd/conf.d/dqsegdb.conf
  sed -i "s/131\.215\.125\.182/${ext_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf
  sed -i "s/10\.14\.0\.117/${int_addr}/g"   /etc/httpd/conf.d/dqsegdb.conf
fi
### Note that dqsegdb.conf will not be changed for segments-other (which doesn't exist; 
###   it's there as a future 'unexpected other case' option)

echo "OPENSSL_ALLOW_PROXY_CERTS=1" >> /etc/sysconfig/httpd 
echo 'PYTHONPATH="/opt/dqsegdb/python_server/src:${PYTHONPATH}"'>> /etc/sysconfig/httpd 


# Import data and create main database.
 
# Create database users and give them privileges
### Note that the ‘empty_database.tgz’ and dqsegdb backups have users ‘dqsegdb_user’ and ‘admin’, 
###      but they don’t work right, so we create the users and give them permissions even before the DB is restored
if [ 1 -eq 0 ]; then
  ### this part probably won't be used again; maybe delete it in a future version
  mysql -e "use dqsegdb"
  mysql -e "REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'dqsegdb_user'@'localhost'"
  mysql -e "DROP USER 'dqsegdb_user'@'localhost'"
  mysql -e "REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'admin'@'localhost'"
  mysql -e "DROP USER 'admin'@'localhost'"
fi
# this part IS done, and is done for all segments machines
mysql -e "CREATE USER 'dqsegdb_user'@'localhost' IDENTIFIED BY 'Q6a6jS6L63RtqnDm'"
mysql -e "GRANT SELECT, INSERT, UPDATE ON dqsegdb.* TO 'dqsegdb_user'@'localhost'"
mysql -e "CREATE USER 'admin'@'localhost' IDENTIFIED BY 'lvdb_11v35'"
mysql -e "GRANT ALL PRIVILEGES ON * . * TO 'admin'@'localhost'"

### Restore an *empty* dqsegdb here
### Note that this will have tables, flags, etc., incl. users ‘dqsegdb_user’ and ‘admin’
if [ 1 -eq 0 ]; then
  ### this part is to restore a *blank* DB, not a backed-up DB
  mkdir /root/empty_database
  cp /backup/segdb/reference/install_support/empty_database.tgz  /root/empty_database/
  cp /backup/segdb/reference/install_support/segments/populate_from_backup.sh  /root/empty_database/
  cd /root/empty_database/
  tar xzf empty_database.tgz
  #/bin/bash ./populate_from_backup.sh
  sudo -u ldbd ./populate_from_backup.sh
fi

### Restore a full backup of dqsegdb here
if [ $host == "segments" ]  || [ $host == "segments-dev" ]
then
  # this part restores a backed-up segments DB
  #mkdir /var/backup_of_dqsegdb/
  tmp_dir=/backup/segdb/segments/install_support/tmp/segments_restore
  mkdir -p  $tmp_dir
  cp /backup/segdb/reference/install_support/segments/populate_from_backup.sh  $tmp_dir
  cp /backup/segdb/segments/primary/*.tar.gz  $tmp_dir
  cd $tmp_dir
  tar xvzf *.tar.gz
  #/bin/bash ./populate_from_backup.sh
  #/bin/bash ./populate_from_backup_manual.sh
  sudo -u ldbd ./populate_from_backup.sh
  rm -rf  $tmp_dir
fi
if [ $host == "segments-backup" ]
then
# this part restores a backed-up segments DB
  #mkdir /var/backup_of_dqsegdb/
  tmp_dir=/backup/segdb/segments/install_support/tmp/segments-backup_restore
  mkdir -p  $tmp_dir
  cp /backup/segdb/reference/install_support/segments-backup/populate_from_backup_segments_backup.sh  $tmp_dir
  cp /backup/segdb/segments/primary/*.tar.gz  $tmp_dir
  cd $tmp_dir
  tar xvzf *.tar.gz
  sudo -u ldbd ./populate_from_backup_segments_backup.sh
  rm -rf  $tmp_dir
# this part restores a backed-up regression test DB
  mkdir -p  $tmp_dir
  cp /backup/segdb/reference/install_support/segments-backup/populate_from_backup_dqsegdb_regression_tests.sh  $tmp_dir
  cp /backup/segdb/segments/regression_tests/dqsegdb_regression_tests_backup.tgz  $tmp_dir
  cd $tmp_dir
  tar xvzf dqsegdb_regression_tests_backup.tgz
  sudo -u ldbd ./populate_from_backup_dqsegdb_regression_tests.sh
  cd /root/
  rm -rf  $tmp_dir
fi


# move certs to appropriate locations, as referenced by /etc/httpd/conf.d/dqsegdb.conf
cp /etc/pki/tls/certs/localhost.crt /etc/pki/tls/certs/localhost.crt.old.$(date +%Y.%m.%d)
cp /etc/pki/tls/private/localhost.key /etc/pki/tls/private/localhost.key.bck.$(date +%Y.%m.%d)
if [ $host == "segments" ] then \
   cp  /backup/segdb/reference/install_support/segments/ldbd*pem  /etc/grid-security/; \
   cp  /backup/segdb/reference/install_support/segments/segments.ligo.org.*  /etc/grid-security/; fi
if [ $host == "segments-backup" ] then \
   cp  /backup/segdb/reference/install_support/segments-backup/segments-backup.ligo.org.*  /etc/grid-security/; fi
if [ $host == "segments-web" ] then \
   cp  /backup/segdb/reference/install_support/segments-web/segments-web.ligo.org.*  /etc/grid-security/;
   mkdir -p /etc/httpd/x509-certs/
   cp  /backup/segdb/reference/install_support/segments-web/segments-web.ligo.org.*  /etc/httpd/x509-certs/; fi
if [ $host == "segments-dev" ] then \
   cp  /backup/segdb/reference/install_support/segments-dev/ldbd*pem  /etc/grid-security/; \
   cp  /backup/segdb/reference/install_support/segments-dev/segments-dev.ligo.org.*  /etc/grid-security/; fi
if [ $host == "segments-s6" ] then \
   cp  /backup/segdb/reference/install_support/segments-s6/segments-s6.ligo.org.*  /etc/grid-security/; fi
cp /etc/grid-security/*.ligo.org.pem /etc/pki/tls/certs/localhost.crt 
cp /etc/grid-security/*.ligo.org.key /etc/pki/tls/private/localhost.key

# Get all cert identifier packages:
yum -y install cilogon-ca-certs
### the above package is no longer available; do we need it (I.e., its replacement) anymore?
yum -y install osg-ca-certs
yum -y install ligo-ca-certs

# Start Apache server.
systemctl enable httpd.service
#chkconfig httpd on   ### old version
systemctl restart httpd.service
#/etc/init.d/httpd restart
# trouble: where does '/usr/lib64/shibboleth/mod_shib_22.so' come from? (Wanted by /etc/httpd/conf.d/shib.conf)


# Add Web Interface configuration.
### which machine(s) use(s) this? create a targeted if-then block for that/those machine(s)
### this was probably from the old segments.ligo.org/web (or whatever it was called) interface)
### nothing should need this anymore; kept just in case
#echo "Alias /dqsegdb_web /usr/share/dqsegdb_web" >> /etc/httpd/conf.d/dqsegdb_web.conf


# more stuff
yum -y install glue lal lal-python python-pyRXP


### Publishing
if [ $host == "segments" ] || [ $host == "segments-dev" ]; then
  ln -s /etc/grid-security/$host.ligo.org.cert /etc/grid-security/robot.cert.pem 
  ln -s /etc/grid-security/$host.ligo.org.key /etc/grid-security/robot.key.pem
  mkdir -p /dqxml/H1
  mkdir -p /dqxml/L1
  mkdir -p /dqxml/V1
  mkdir -p /dqxml/G1
  cp  /backup/segdb/reference/install_support/etc_init.d_dir/dqxml_pull_from_obs  /etc/init.d/
  cp  /backup/segdb/reference/install_support/root_bin_dir/dqxml_pull_from_obs  /root/bin/
  cp  /backup/segdb/reference/install_support/ligolw_dtd.txt  /root/bin/
  cp  /backup/segdb/reference/install_support/dqsegdb_September_11_2018.tgz  /root/
  ### should we be installing this from github, rather than a static file?
  cd /root/
  tar xzf dqsegdb_September_11_2018.tgz
  if [ $host == "segments" ]
  then
    cd /root/bin/
    cp  /backup/segdb/reference/root_files/segments/bin/run_publishing_O3_segmentsligoorg.sh_new_2019.01.01  .
    ln -s  run_publishing_O3_segmentsligoorg.sh_new_2019.01.01  run_publishing_O3_segmentsligoorg.sh
    cp /backup/segdb/reference/root_files/segments/bin/lstatus*  .
  fi
  if [ $host == "segments-dev" ]
  then
    cd /root/bin/
    cp  /backup/segdb/reference/root_files/segments-dev/bin/run_publishing_O3_segmentsdevligoorg.sh_new_2019.01.01  .
    ln -s  run_publishing_O3_segmentsdevligoorg.sh_new_2019.01.01  run_publishing_O3_segmentsdevligoorg.sh
    cp /backup/segdb/reference/root_files/segments-dev/bin/lstatus*  .
  fi
  mkdir -p /var/log/publishing/dev/
  mkdir -p /var/log/publishing/state/
  mkdir -p /var/log/publishing/pid/
  if [ 0 -eq 1 ]; then
    ### this wouldn't be done for a regular installation
    cp /backup/segdb/segments-dev/install/blank-DQ_Segments_current_dev.xml  /var/log/publishing/state/
    cp /backup/segdb/segments-dev/install/blank-DQ_Segments_current_dev.xml  /var/log/publishing/state/H-DQ_Segments_current_dev.xml
    cp /backup/segdb/segments-dev/install/blank-DQ_Segments_current_dev.xml  /var/log/publishing/state/L-DQ_Segments_current_dev.xml
    cp /backup/segdb/segments-dev/install/blank-DQ_Segments_current_dev.xml  /var/log/publishing/state/V-DQ_Segments_current_dev.xml
    cp /backup/segdb/segments-dev/install/blank-DQ_Segments_current_dev.xml  /var/log/publishing/state/G-DQ_Segments_current_dev.xml
  fi
  #latest_state_dir=`ls -1tr /backup/segdb/segments/publisher/spool/ | tail -n 1`
  latest_state_dir=`ls -1tr /backup/segdb/segments/publisher/spool/ | tail -n 2 | head -n 1`
    ### would it be better to go back one day for state files, to be safe? then just re-publish that one day's segments? 
    ### if so, replace 'tail -n 1' with 'tail -n 2 | head -n 1'
    ### DB backup is done at 00:00; 'spool_backup' is done at 00:07; that means that ~7 minutes of segments will be
    ###   recorded in the state file, but won't show up in the backup
  cp /backup/segdb/segments/publisher/spool/$latest_state_dir/*  /var/log/publishing/state/

  ### something looks for the ligolw_dtd.txt file here, doesn't it? (check; if not, get rid of this)
  mkdir -p /root/Publisher/etc/
  cp  /backup/segdb/reference/install_support/ligolw_dtd.txt  /root/Publisher/etc/
  
  cp  /backup/segdb/reference/lgmm/grid-mapfile-insert  /etc/grid-security/

  if [ $live -eq 1 ]
  then
    /sbin/chkconfig  dqxml_pull_from_obs  on
    systemctl start dqxml_pull_from_obs.service
    if [ $host == "segments" ]
    then 
      /sbin/chkconfig  dqxml_push_to_ifocache  on 
      systemctl start dqxml_pull_from_obs.service
    fi
  fi
  # create some useful links
  ln -s /root/bin/dqsegdb_September_11_2018   /root/bin/dqsegdb_current_code
  ln -s /var/log/publishing/state/   /root/bin/state_files
  ln -s /var/log/publishing/pid/   /root/bin/pid_files
  ln -s /var/log/publishing/dev  /root/bin/publisher_log_files
fi


# create crontab files
# first, backup any existing cron files that would be overwritten (though there shouldn't be any)
if [ -e /var/spool/cron/root ]; then cp /var/spool/cron/root /root/cron_root_bak_$(date +%Y.%m.%d) ; fi
if [ -e /var/spool/cron/ldbd ]; then cp /var/spool/cron/ldbd /root/cron_ldbd_bak_$(date +%Y.%m.%d) ; fi
if [ $host == "segments" ] || [ $host == "segments-dev" ] || [ $host == "segments-backup" ]
then
  if [ $live -eq 1 ]; then
    cp  `ls -1rt /backup/segdb/reference/root_files/$host/crontab_-l_root* | tail -n 1` /var/spool/cron/root
    cp  `ls -1rt /backup/segdb/reference/ldbd_files/$host/crontab_-l_ldbd* | tail -n 1` /var/spool/cron/ldbd
  else
    cp  `ls -1rt /backup/segdb/reference/root_files/$host/crontab_-l_root*all_lines_commented* | tail -n 1` /var/spool/cron/root
    cp  `ls -1rt /backup/segdb/reference/ldbd_files/$host/crontab_-l_ldbd*all_lines_commented* | tail -n 1` /var/spool/cron/ldbd
  fi
  # create dir to hold files that are created by a cron job, then grabbed by Nagios, for use on monitor.ligo.org:
  if [ $host == "segments" ] && [ ! -d /var/www/nagios/ ]; then mkdir -p /var/www/nagios/ ; fi
fi
# Note that there are currently (Jan. 2019) no crontabs for any users on segments-web or segments-dev2, 
#   and segments-s6 is likely to be decommissioned very soon, so it does not need to be handled.


# create some useful links
# format reminder: 'ln -s [actual_file]   [link_name]'
ln -s /var/log/httpd/   /root/bin/httpd_logs
ln -s /opt/dqsegdb/python_server/logs/ /root/bin/python_server_log_files


# run some machine-specific items
if [ $host == "segments" ]
then
  mkdir -p /usr1/ldbd/
  mkdir -p /usr1/ldbd/bin
  cp -rp  /backup/segdb/reference/ldbd_files/$host/bin/*  /usr1/ldbd/bin/
  chown -R ldbd:ldbd /usr1/ldbd
  cp -rp  /backup/segdb/reference/install_support/segments/root_bin/*  /root/bin/
  ### this source dir doesn't exist yet
  # what else?
fi
if [ $host == "segments-backup" ]
then
  mkdir -p /usr1/ldbd/
  mkdir -p /usr1/ldbd/bin
  mkdir -p /usr1/ldbd/backup_logging
  cp -rp  /backup/segdb/segments/backup_logging/*  /usr1/ldbd/backup_logging/
  cp -rp  /backup/segdb/reference/ldbd_files/$host/bin/*  /usr1/ldbd/bin/
  chown -R ldbd:ldbd /usr1/ldbd
  cp -rp  /backup/segdb/reference/install_support/segments-backup/root_bin/*  /root/bin/
  # Restore the saved regression tests DB
  mkdir /var/backup_of_dqsegdb/
  cp /backup/segdb/reference/install_support/segments/populate_from_backup.sh  /var/backup_of_dqsegdb/
  cp /backup/segdb/segments/primary/*.tar.gz  /var/backup_of_dqsegdb/
  cd /var/backup_of_dqsegdb/
  tar xvzf *.tar.gz
  #/bin/bash ./populate_from_backup.sh
  #/bin/bash ./populate_from_backup_manual.sh
  sudo -u ldbd ./populate_from_backup.sh
# what else?
fi
if [ $host == "segments-web" ]
then
  cp -rp  /backup/segdb/reference/install_support/segments-web/root_bin/*  /root/bin/
  ### this source dir doesn't exist yet
  # what else?
fi
if [ $host == "segments-dev" ]
then
  mkdir -p /usr1/ldbd/
  mkdir -p /usr1/ldbd/bin
  cp -rp  /backup/segdb/reference/ldbd_files/$host/bin/*  /usr1/ldbd/bin/
  chown -R ldbd:ldbd /usr1/ldbd
  cp -rp  /backup/segdb/reference/install_support/segments-dev/root_bin/*  /root/bin/
  ### this source dir doesn't exist yet
  # what else?
fi
# note: no user 'ldbd' used on segments-web; we aren't planning to ever restore segments-s6; segments-dev2 is done manually


# something about adding the cert to grid-mapfile and grid-mapfile-insert in /etc/grid-security/
 
# something about backups


### User tasks to be performed manually:
# looks like there aren't any anymore...


exit


### to do:
### * make sure that grid-mapfile gets created, and with proper ownership and permissions
### * Start a new dir for httpd, with contents selected from 
###     the line "rsync -avP /backup/segdb/segments/install_support/conf.d   /etc/httpd/", above
### * Set up files for /etc/httpd/conf.d/ for segments-web
### * 



